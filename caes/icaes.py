import pandas as pd
from caes import CAES
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function


class ICAES(CAES):
    def __init__(self, ML=1.0, depth=1000.0):
        """
        Initializes a 3 stage near-isothermal CAES system
        """
        CAES.__init(self)

        # Mass loading
        self.ML = ML

        # reservoir
        self.depth = depth

        # pump
        self.eta_pump = 0.75

        # stage pressure ratios
        self.PR1 = 6.0
        self.PR2 = 6.0
        self.PR3 = 6.0

        # stage number of nozzles
        self.nozzles1 = 1
        self.nozzles2 = 5
        self.nozzles3 = 15

        # recreate dataframe to store data (with additional entries)
        additional_time_series = ['w_1', 'w_2', 'w_3', 'w_pmp1', 'w_pmp2', 'w_pmp3', 'T1', 'T2', 'T3', 'T4']
        self.attributes_time_series = self.attributes_time_series + additional_time_series
        self.data = pd.DataFrame(data=0.0, columns=self.attributes_time_series)

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
        air = 'AIR.MIX'
        cd = self.c_water

        # --------------
        # inlet
        # --------------
        p1 = self.p_atm
        T1 = self.T_atm

        # --------------
        # low pressure stage (1 -> 2)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T1, 'P', p1, air)  # constant pressure specific heat [J/kg-K]
        cv = CP.PropsSI('CVMASS', 'T', T1, 'P', p1, air)  # constrant volume specific heat [J/kg-K]
        k = cp / cv  # heat capacity ratio [-]
        # calcs
        p2 = p1 * self.PR1  # outlet pressure
        ML1 = self.nozzles1 * (1.65 * 1e-3 / p2 - 0.05)  # mass loading
        n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))  # polytropic exponent
        T2 = T1 * (p2 / p1) ** ((n1 - 1.0) / n1)  # outlet temperature

        # --------------
        # medium pressure stage  (2 -> 3)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T2, 'P', p2, air)
        cv = CP.PropsSI('CVMASS', 'T', T2, 'P', p2, air)
        k = cp / cv
        # calcs
        p3 = p2 * self.PR2
        ML2 = self.nozzles2 * (1.65 * 1e-3 / p3 - 0.05)
        n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML2 * (cd / cp))
        T3 = T2 * (p3 / p2) ** ((n2 - 1.0) / n2)

        # --------------
        # high pressure stage  (3 -> 4)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T3, 'P', p3, air)
        cv = CP.PropsSI('CVMASS', 'T', T3, 'P', p3, air)
        k = cp / cv
        # calcs
        p4 = self.p_store
        ML3 = self.nozzles3 * (1.65 * 1e-3 / p4 - 0.05)
        n3 = k * (1 + ML3 * (cd / cp)) / (1 + k * ML3 * (cd / cp))
        T4 = T3 * (p4 / p3) ** ((n3 - 1.0) / n3)

        # --------------
        # work, work = R / (M * (1-n)) * (T2 - T1)
        # --------------
        w_1 = self.R / (self.M * (1 - n1)) * (T2 - T1)
        w_2 = self.R / (self.M * (1 - n2)) * (T3 - T2)
        w_3 = self.R / (self.M * (1 - n3)) * (T4 - T3)

        # --------------
        # pump work, = ML * v * (p2 - p1) / eta_pump
        # --------------
        w_pmp1 = - ML1 * self.v_water * (p2 - p1) / self.eta_pump
        w_pmp2 = - ML2 * self.v_water * (p3 - p2) / self.eta_pump
        w_pmp3 = - ML3 * self.v_water * (p4 - p3) / self.eta_pump

        # --------------
        # store results
        # --------------
        # required
        s['work_per_kg'] = w_1 + w_2 + w_3 + w_pmp1 + w_pmp2 + w_pmp3
        s['water_per_kg'] = ML1 + ML2 + ML3
        s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input
        # additional
        s['w_1'] = w_1
        s['w_2'] = w_2
        s['w_3'] = w_3
        s['w_pmp1'] = w_pmp1
        s['w_pmp2'] = w_pmp2
        s['w_pmp3'] = w_pmp3
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
        air = 'AIR.MIX'
        cd = self.c_water

        # --------------
        # inlet
        # --------------
        p4 = self.p_store
        T4 = self.T_store

        # --------------
        # high pressure stage (4 -> 3)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T4, 'P', p4, air)  # constant pressure specific heat [J/kg-K]
        cv = CP.PropsSI('CVMASS', 'T', T4, 'P', p4, air)  # constrant volume specific heat [J/kg-K]
        k = cp / cv  # heat capacity ratio [-]
        # calcs
        p3 = p4 / self.PR3  # outlet pressure
        ML3 = self.nozzles3 * (1.65 * 1e-3 / p4 - 0.05)  # stage mass loading
        n3 = k * (1 + ML3 * (cd / cp)) / (1 + k * ML3 * (cd / cp))  # polytropic exponent
        T3 = T4 * (p4 / p3) ** ((n3 - 1.0) / n3)  # outlet temperature

        # --------------
        # medium pressure stage (3 -> 2)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T3, 'P', p3, air)
        cv = CP.PropsSI('CVMASS', 'T', T3, 'P', p3, air)
        k = cp / cv
        # calcs
        p2 = p3 / self.PR2
        ML2 = self.nozzles2 * (1.65 * 1e-3 / p3 - 0.05)
        n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML2 * (cd / cp))
        T2 = T3 * (p3 / p2) ** ((n2 - 1.0) / n2)

        # --------------
        # low pressure stage (2 -> 1)
        # --------------
        # fluid properties
        cp = CP.PropsSI('CPMASS', 'T', T2, 'P', p2, air)
        cv = CP.PropsSI('CVMASS', 'T', T2, 'P', p2, air)
        k = cp / cv
        # calcs
        p1 = self.p_atm
        ML1 = self.nozzles1 * (1.65 * 1e-3 / p2 - 0.05)
        n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))
        T1 = T2 * (p2 / p1) ** ((n1 - 1.0) / n1)

        # --------------
        # calculate work, work = R / (M * (1-n)) * (T1 - T2)
        # --------------
        w_1 = self.R / (self.M * (1 - n1)) * (T1 - T2)
        w_2 = self.R / (self.M * (1 - n2)) * (T2 - T3)
        w_3 = self.R / (self.M * (1 - n3)) * (T3 - T4)

        # --------------
        # pump work, = ML * v * (p2 - p1) / eta_pump
        # --------------
        w_pmp1 = - ML1 * self.v_water * (p2 - p1) / self.eta_pump
        w_pmp2 = - ML2 * self.v_water * (p3 - p2) / self.eta_pump
        w_pmp3 = - ML3 * self.v_water * (p4 - p3) / self.eta_pump

        # --------------
        # store results
        # --------------
        # required
        s['work_per_kg'] = w_1 + w_2 + w_3 + w_pmp1 + w_pmp2 + w_pmp3
        s['water_per_kg'] = ML1 + ML2 + ML3
        s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input
        # additional
        s['w_1'] = w_1
        s['w_2'] = w_2
        s['w_3'] = w_3
        s['w_pmp1'] = w_pmp1
        s['w_pmp2'] = w_pmp2
        s['w_pmp3'] = w_pmp3
        s['T1'] = T1
        s['T2'] = T2
        s['T3'] = T3
        s['T4'] = T4

        return s
