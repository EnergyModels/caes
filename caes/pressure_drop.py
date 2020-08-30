from math import log, log10, pi


def aquifer_dp(Q=1, r_f=100.0, r_w=0.25, k=100, mu=0.5, h=40.0, p_f=10.0, T=298.15, Z=1.0):
    """
    # Q - radial flow rate[m3 / s]
    # P - pressure(f - formation edge, s - wellbore) [MPa]
    # R - radius(f - formation, w - wellbore)[m]
    # H - formation height[m]
    # K - permeability[mD]
    # Mu - viscosity[cP]
    # Z - gas deviation factor[-]
    """
    quantity = p_f ** 2.0 - Q * mu * T * Z * log(r_f / r_w) / (8.834 * 10.0 ** -3.0 * k * h)
    if quantity > 0.0:
        delta_p = p_f - quantity ** 0.5
    else:
        delta_p = 1e12 # would have been a complex number, make pressure drop extremely large
        print('Warning - Very large aquifer pressure drop')

    return delta_p


def friction_coeff(Re=1000.0, epsilon=0.002 * 1e-3, d=1.06):
    """

    :param Re: Reynolds number [-]
    :param epsilon: Pipe roughness [m]
    :param d: Pipe diameter [m]
    :return f: friction coefficient [-]
    """
    if Re == 0.0:
        f = 0.0
    elif Re <= 4000:  # laminar flow
        f = 64.0 / Re

    else:  # turbulent flow
        # allowable calculation error
        error = 1e-6

        # initial friction factor values
        f = 0.01  # initial guess

        # initial values
        LHS = 1.0
        RHS = 0.0

        while abs(LHS - RHS) > error:
            # f_guess = f_calc  # update guess
            # a =
            # f_calc = (1 / a) ** 2  # calculate new value

            LHS = 1 / (f ** 0.5)
            RHS = -2.0 * log10((epsilon / d) / 3.7 + 2.51 / (Re * f ** 0.5))
            f = (1 / RHS) ** 2  # calculate new value

    return f


def pipe_fric_dp(epsilon=0.002 * 1.0e-3, d=1.06, depth=950, m_dot=10.0, rho=172, mu=18.37e-6):
    """
    Assumes constant density
    :param epsilon: roughness [m]
    :param d: pipe diameter [m]
    :param depth: well depth / pipe length [m]
    :param m_dot: mass flow [kg/s]
    :param rho: density [kg/m^3]
    :param mu: viscosity [Pa*s]
    :return delta_p: pressure drop [MPa]
    """

    # gravitational constant
    g = 9.81  # [m/s^2]

    if abs(m_dot) == 0.0:  # no flow
        delta_p = 0.0
        f = 0.0
    else:

        # velocity
        A = pi / 4.0 * d ** 2.0  # pipe cross-sectional area [m^2]
        U = m_dot / (rho * A)  # velocity [m/s]

        # Reynolds number
        Re = rho * d * abs(U) / mu

        f = friction_coeff(Re=Re, epsilon=epsilon, d=d)

        # head loss
        h = f * depth / d * U ** 2.0 / (2.0 * g)

        # pressure drop
        delta_p = rho * g * h

    return delta_p * 1.0e-6, f  # convert from Pa to MPa


def pipe_grav_dp(m_dot=10.0, rho=115.0, z=950.0):
    """

    :param m_dot: mass flow [kg/s], (+) injection, (-) withdrawl
    :param rho: density [kg/m^3]
    :param z: depth/length [m]
    :return delta_p: pressure loss [MPa]
    """

    # gravitational constant
    g = 9.81  # [m/s^2]

    if m_dot > 0.0:  # injection
        delta_p = -rho * g * z
    elif m_dot < 0.0:  # withdrawl
        delta_p = rho * g * z
    else:  # no activity
        delta_p = -rho * g * z

    return delta_p * 1.0e-6  # convert from Pa to MPa
