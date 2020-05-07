import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import pi


def wellbore(T_air_in, p_air_in, depth, D, m_dot, direction='in', f=0.015):
    """
    Simulates the friction pressure drop of a wellbore using the Darcy-Weisbach equation

    Parameters:
        T_air_in [K]
        p_air_in [Pa]
        depth - wellbore length/depth [m]
        D - wellbore diameter [m]
        m_dot - mass flow rate [kg/s]
        direction - in/out [-]
        f - friction coefficient [-]

    Returns:
        delta_p - pressure drop [Pa]

    """

    # define fluids
    air = 'AIR.MIX'

    # fluid properties
    rho = CP.PropsSI('D', 'T', T_air_in, 'P', p_air_in, air)  # density [kg/m3]
    g = 9.81  # gravitational constant [m/s^2]

    # air velocity
    A = pi * (D / 2.0) ** 2.0
    V = m_dot / (rho * A)

    # calculate pressure drop
    if direction == 'out':
        delta_p = rho * g * depth + f * depth / D * rho * V ** 2.0 / 2.0
    else:  # in
        delta_p = rho * g * depth + f * depth / D * rho * V ** 2.0 / 2.0

    # calculate pressure drop
    delta_p = f * depth / D * rho * V ** 2.0 / 2.0
    return delta_p
