from caes import CAES, isothermal_cmp, isothermal_exp
from CoolProp.CoolProp import PropsSI


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

        # pressures
        p1 = self.p_atm
        p2 = p1 * self.PR1
        p3 = p2 * self.PR2
        p4 = self.p_store

        # mass loading
        ML1 = self.nozzles1 * (1.65 * 1e-3 / p2 - 0.05)
        ML2 = self.nozzles2 * (1.65 * 1e-3 / p3 - 0.05)
        ML3 = self.nozzles3 * (1.65 * 1e-3 / p4 - 0.05)

        # polytropic exponent
        n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))
        n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML1 * (cd / cp))
        n3 = k * (1 + ML3 * (cd / cp)) / (1 + k * ML1 * (cd / cp))

        # temperatures
        T1 = self.T_atm
        T2 = T1 * (p2 / p1) ** ((n1 - 1.0) / n1)
        T3 = T2 * (p3 / p2) ** ((n2 - 1.0) / n2)
        T4 = T3 * (p4 / p3) ** ((n3 - 1.0) / n3)

        # idealized isothermal process
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(self.p_atm / self.p_store)
        s['water_per_kg'] = 0.0  # idealized process - no cooling water
        s['fuel_per_kg'] = 0.0  # isothermal - no heat input

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
        # pressures
        p4 = self.p_store
        p3 = p4 / self.PR3
        p2 = p3 / self.PR2
        p1 = self.p_atm

        # idealized isothermal process
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(self.p_store / self.p_atm)
        s['water_per_kg'] = 0.0  # idealized process - no cooling water
        s['fuel_per_kg'] = 0.0  # isothermal - no heat input

        return s
