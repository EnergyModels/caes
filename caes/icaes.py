from caes import CAES
from CoolProp.CoolProp import PropsSI


class ICAES(CAES):
    def __init__(self, ML=1.0):
        CAES.__init(self)

        # Mass loading
        self.ML = ML

    def charge(self, s):
        # update for each caes architecture
        pwr_request = abs(s['pwr_request'])

        # TODO get thermodynamic properties
        # TODO eff = f(ML)

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
