import pandas as pd
from caes import CAES
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function


class ICAES(CAES):
    def get_default_inputs():
        inputs = CAES.get_default_inputs()
        inputs['depth'] = 2.0
        inputs['ML'] = 1.0
        inputs['nozzles1'] = 1.0
        inputs['nozzles2'] = 5.0
        inputs['nozzles3'] = 15.0
        return inputs

    def __init__(self, inputs=get_default_inputs()):
        """
        Initializes a 3 stage near-isothermal CAES system
        """
        CAES.__init__(self, inputs)

        # Mass loading
        self.ML = inputs['ML']

        # reservoir
        self.depth = inputs['depth']

        # fluid properties
        self.cp = CP.PropsSI('CPMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR.MIX') / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.cv = CP.PropsSI('CVMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR.MIX') / 1000.0  # constant volume specific heat [kJ/kg-K]
        self.k = self.cp / self.cv  # heat capacity ratio [-]

        # pump
        self.eta_pump = 0.75

        # stage pressure ratios # equally divide among stages
        self.PR1 = (self.p_store_max / self.p_atm) ** (1. / 3.)
        self.PR2 = (self.p_store_max / self.p_atm) ** (1. / 3.)
        self.PR3 = (self.p_store_max / self.p_atm) ** (1. / 3.)

        # stage number of nozzles
        self.nozzles1 = inputs['nozzles1']
        self.nozzles2 = inputs['nozzles2']
        self.nozzles3 = inputs['nozzles3']

        # recreate dataframe to store data (with additional entries)
        additional_time_series = ['ML1', 'ML2', 'ML3', 'n1', 'n2', 'n3',
                                  'w_1', 'w_2', 'w_3', 'w_pmp1', 'w_pmp2', 'w_pmp3',
                                  'p1', 'p2', 'p3', 'p4',
                                  'T1', 'T2', 'T3', 'T4']
        self.attributes_time_series = self.attributes_time_series + additional_time_series
        self.data = pd.DataFrame(columns=self.attributes_time_series)

    def charge_perf(self, s):
        """

        charge_perf - performance of compressors to store energy

        designed to be updated for each caes architecture

        :param:
            s - pandas series containing performance of current time step and error messages
        :return:
            s - updated including (at a minimum) the following entries:
                work_per_kg - compression work [kJ/kg air]
                water_per_kg - water use [kg water /kg air ]
                fuel_per_kg - fuel use [kg fuel /kg air]
        """
        # --------------
        # fluid properties
        # --------------
        cd = self.c_water  # water - heat capacity [kJ/kg-K]
        cp = self.cp  # air - constant pressure specific heat [kJ/kg-K]
        k = self.k  # air - heat capacity ratio [-]

        # --------------
        # inlet
        # --------------
        p1 = self.p_atm
        T1 = self.T_atm

        # --------------
        # determine stage outlet pressures
        # --------------
        p4 = self.p_store  # final outlet pressure always at storage pressure
        if (p1 * self.PR1) >= p4:  # check if LP stage alone is sufficient
            p2 = p4
            p3 = p4
        else:
            p2 = p1 * self.PR1
            if (p2 * self.PR2) >= p4:  # check if LP and MP stages togehter are sufficient
                p3 = p4
            else:
                p3 = p2 * self.PR2

        # --------------
        # low pressure stage (1 -> 2)
        # --------------

        ML1 = self.nozzles1 * (1.65 * 1e3 / p2 - 0.05)  # mass loading
        n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))  # polytropic exponent
        T2 = T1 * (p2 / p1) ** ((n1 - 1.0) / n1)  # outlet temperature

        # --------------
        # medium pressure stage  (2 -> 3)
        # --------------
        if p2 == p4:  # check if this stage is needed
            ML2 = 0.0
            n2 = 0.0
            T3 = T2
        else:

            ML2 = self.nozzles2 * (1.65 * 1e3 / p3 - 0.05)
            n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML2 * (cd / cp))
            T3 = T2 * (p3 / p2) ** ((n2 - 1.0) / n2)

        # --------------
        # high pressure stage  (3 -> 4)
        # --------------
        if p3 == p4:  # check if this stage is needed
            ML3 = 0.0
            n3 = 0.0
            T4 = T3
        else:
            ML3 = self.nozzles3 * (1.65 * 1e3 / p4 - 0.05)
            n3 = k * (1 + ML3 * (cd / cp)) / (1 + k * ML3 * (cd / cp))
            T4 = T3 * (p4 / p3) ** ((n3 - 1.0) / n3)

        # --------------
        # work, work = R / (M * (1-n)) * (T2 - T1)
        # --------------
        w_1 = self.R / (self.M * (1 - n1)) * (T2 - T1)  # [kJ/kg]
        w_2 = self.R / (self.M * (1 - n2)) * (T3 - T2)  # [kJ/kg]
        w_3 = self.R / (self.M * (1 - n3)) * (T4 - T3)  # [kJ/kg]

        # --------------
        # pump work, = ML * v * (p2 - p1) / eta_pump
        # --------------
        w_pmp1 = - ML1 * self.v_water * (p2 - p1) / self.eta_pump / 1000.0  # [kJ/kg]
        w_pmp2 = - ML2 * self.v_water * (p3 - p1) / self.eta_pump / 1000.0  # [kJ/kg]
        w_pmp3 = - ML3 * self.v_water * (p4 - p1) / self.eta_pump / 1000.0  # [kJ/kg]

        # --------------
        # store results
        # --------------
        # required
        s['work_per_kg'] = w_1 + w_2 + w_3 + w_pmp1 + w_pmp2 + w_pmp3  # [kJ/kg]
        s['water_per_kg'] = ML1 + ML2 + ML3  # [kg/kg air]
        s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
        # additional
        s['ML1'] = ML1
        s['ML2'] = ML2
        s['ML3'] = ML3
        s['n1'] = n1
        s['n2'] = n2
        s['n3'] = n3
        s['w_1'] = w_1
        s['w_2'] = w_2
        s['w_3'] = w_3
        s['w_pmp1'] = w_pmp1
        s['w_pmp2'] = w_pmp2
        s['w_pmp3'] = w_pmp3
        s['p1'] = p1
        s['p2'] = p2
        s['p3'] = p3
        s['p4'] = p4
        s['T1'] = T1
        s['T2'] = T2
        s['T3'] = T3
        s['T4'] = T4

        return s

    def discharge_perf(self, s):
        """
        discharge_perf - performance of expanders to release energy from storage

        designed to be updated for each caes architecture

        :param:
            s - pandas series containing performance of current time step and error messages
        :return:
            s - updated including (at a minimum) the following entries:
                work_per_kg - compression work [kJ/kg air]
                water_per_kg - water use [kg water /kg air ]
                fuel_per_kg - fuel use [kg fuel /kg air]
        """
        # --------------
        # fluid properties
        # --------------
        cd = self.c_water  # water - heat capacity [kJ/kg-K]
        cp = self.cp  # air - constant pressure specific heat [kJ/kg-K]
        k = self.k  # air - heat capacity ratio [-]

        # --------------
        # inlet
        # --------------
        p4 = self.p_store
        T4 = self.T_store

        # --------------
        # determine stage outlet pressures
        # --------------
        p1 = self.p_atm  # final outlet pressure always at atmospheric pressure
        if (p4 / self.PR3) <= p1:  # check if HP stage alone is sufficient
            p3 = p1
            p2 = p1
        else:
            p3 = p4 / self.PR3
            if (p3 / self.PR2) <= p1:  # check if HP and MP stages together are sufficient
                p2 = p1
            else:
                p2 = p3 / self.PR2

        # --------------
        # high pressure stage (4 -> 3)
        # --------------
        ML3 = self.nozzles3 * (1.65 * 1e3 / p4 - 0.05)  # stage mass loading
        n3 = k * (1 + ML3 * (cd / cp)) / (1 + k * ML3 * (cd / cp))  # polytropic exponent
        T3 = T4 * (p4 / p3) ** ((n3 - 1.0) / n3)  # outlet temperature

        # --------------
        # medium pressure stage (3 -> 2)
        # --------------
        if p3 == p4:  # check if this stage is needed
            ML2 = 0.0
            n2 = 0.0
            T2 = T3
        else:
            ML2 = self.nozzles2 * (1.65 * 1e3 / p3 - 0.05)
            n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML2 * (cd / cp))
            T2 = T3 * (p3 / p2) ** ((n2 - 1.0) / n2)

        # --------------
        # low pressure stage (2 -> 1)
        # --------------
        if p3 == p4:  # check if this stage is needed
            ML1 = 0.0
            n1 = 0.0
            T1 = T2
        else:
            ML1 = self.nozzles1 * (1.65 * 1e3 / p2 - 0.05)
            n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))
            T1 = T2 * (p2 / p1) ** ((n1 - 1.0) / n1)

        # --------------
        # calculate work, work = R / (M * (1-n)) * (T2 - T1)
        # --------------
        w_1 = self.R / (self.M * (1 - n1)) * (T2 - T1)
        w_2 = self.R / (self.M * (1 - n2)) * (T3 - T2)
        w_3 = self.R / (self.M * (1 - n3)) * (T4 - T3)

        # --------------
        # pump work, = ML * v * (p2 - p1) / eta_pump
        # --------------
        w_pmp1 = - ML1 * self.v_water * (p2 - p1) / self.eta_pump / 1000.0  # [kJ/kg]
        w_pmp2 = - ML2 * self.v_water * (p3 - p1) / self.eta_pump / 1000.0  # [kJ/kg]
        w_pmp3 = - ML3 * self.v_water * (p4 - p1) / self.eta_pump / 1000.0  # [kJ/kg]

        # --------------
        # store results
        # --------------
        # required
        s['work_per_kg'] = w_1 + w_2 + w_3 + w_pmp1 + w_pmp2 + w_pmp3  # [kJ/kg]
        s['water_per_kg'] = ML1 + ML2 + ML3  # [kg/kg air]
        s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
        # additional
        s['ML1'] = ML1
        s['ML2'] = ML2
        s['ML3'] = ML3
        s['n1'] = n1
        s['n2'] = n2
        s['n3'] = n3
        s['w_1'] = w_1
        s['w_2'] = w_2
        s['w_3'] = w_3
        s['w_pmp1'] = w_pmp1
        s['w_pmp2'] = w_pmp2
        s['w_pmp3'] = w_pmp3
        s['p1'] = p1
        s['p2'] = p2
        s['p3'] = p3
        s['p4'] = p4
        s['T1'] = T1
        s['T2'] = T2
        s['T3'] = T3
        s['T4'] = T4

        return s
