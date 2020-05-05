from caes import CAES
from CoolProp.CoolProp import PropsSI
from .isothermal_components import isothermal_cmp, isothermal_exp


class ICAES(CAES):
    def __init__(self, ML=1.0):
        CAES.__init(self)

        # Mass loading
        self.ML = ML

        # reservoir

    def charge(self, s):
        # update for each caes architecture
        pwr_request = abs(s['pwr_request'])

        # TODO get thermodynamic properties
        # TODO eff = f(ML)

        # LP compressor
        T_air_out, w_total, w_cmp, w_pmp = isothermal_cmp(ML, T_air_in, p_air_in, p_air_out, T_water_in, p_water_in, eta_pump)

        # HP compressor
        T_air_out, w_total, w_cmp, w_pmp = isothermal_cmp(ML, T_air_in, p_air_in, p_air_out, T_water_in, p_water_in,
                                                          eta_pump)


        # reservoir
        # use energy storage ratio from Li et al and Guo et al. and Oldenburg and Pan
        p1
        p2
        p3



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
