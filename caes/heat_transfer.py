from math import pi, exp


def pipe_heat_transfer(d=1.06, m_dot=10.0, rho=172, mu=18.37e-6, Pr=0.1, k=0.1, cp=1.0, depth=1402.0, Tm=290.0,
                       Ts=290.0):
    """
    Assumes constant density
    :param Ts:
    :param Pr:
    :param Tm:
    :param k:
    :param cp:
    :param d: pipe diameter [m]
    :param depth: well depth / pipe length [m]
    :param m_dot: mass flow [kg/s]
    :param rho: density [kg/m^3]
    :param mu: viscosity [Pa*s]
    :return delta_p: pressure drop [MPa]
    """

    # Reynolds number
    A = pi / 4.0 * d ** 2.0  # pipe cross-sectional area [m^2]
    U = m_dot / (rho * A)  # velocity [m/s]
    Re = rho * d * abs(U) / mu  # [-]

    # Nusselt Number
    if Ts > Tm:  # heating
        n = 0.4
    else:  # cooling
        n = 0.3
    Nu = 0.023 * Re ** (4.0 / 5.0) * Pr ** n  # [-]

    # Heat transfer coefficient
    h = Nu * k / d  # [W/m^2*K]

    # heat transfer
    SA = depth * pi * d  # pipe surface area [m^2]
    # q = h * SA * (Tm - Ts)  # [W=J/s]
    # # delta_t = depth / U  # time to travel pipe length [s]
    # # Q = q * delta_t  # heat transferred [J]
    # delta_T = q / (m_dot * cp)
    Tm_out = Ts - (Ts - Tm) * exp(-(SA * h)/(abs(m_dot)*cp))
    delta_T = Tm - Tm_out

    return delta_T
