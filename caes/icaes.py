from caes import CAES, isothermal_cmp, isothermal_exp
from CoolProp.CoolProp import PropsSI


class ICAES(CAES):
    def __init__(self, ML=1.0, depth=1000.0):
        CAES.__init(self)

        # Mass loading
        self.ML = ML

        # reservoir
        self.depth = depth

        # pump
        self.eta_pump = 0.75

    def charge(self, s):
        # update for each caes architecture
        pwr_request = abs(s['pwr_request'])

        # LP compressor
        p2 =
        T2, w_total_lp, w_cmp_lp, w_pmp_lp = isothermal_cmp(self.ML, self.T_amb, self.p_amb, p2, self.T_water, self.p_water, self.eta_pump)

        # HP compressor
        p3 =
        T3, w_total_hp, w_cmp_hp, w_pmp_hp = isothermal_cmp(self.ML, T2, p2, p3, self.T_water, self.p_water, self.eta_pump)


        # reservoir
        # use energy storage ratio from Li et al and Guo et al. and Oldenburg and Pan
        p1
        p2
        p3


        m = m +


        # work
        w = n


        # compressor HP stage (state 2 to 3)



        fluid = 'Air.mix'

        ML =
        k
        cd =
        cp =
        cv = PropsSI('T','P')




        # calculate
        s['pwr_input'] = pwr_request
        s['pwr_output'] = 0.0
        s['heat_input'] = 0.0  # heat not used in ICAES
        s['m_air'] = 0.0
        s['m_water'] = s['m_air'] * self.ML

        return s

    def discharge(self, s):
        # update for each caes architecture
        pwr_request = abs(s['pwr_request'])

        # calculate
        s['pwr_input'] = 0.0
        s['pwr_output'] = pwr_request
        s['heat_input'] = 0.0  # heat not used in ICAES
        s['m_air'] = 0.0
        s['m_water'] = s['m_air'] * self.ML
        return s
