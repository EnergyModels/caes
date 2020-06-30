from math import log, pi


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
    delta_p = p_f - (p_f ** 2 - Q * mu * T * Z * log(r_f / r_w) / (8.834 * 10 ** -3 * k * h)) ** 0.5

    return delta_p


def friction_coeff(Re=1000.0, epsilon=0.002 * 1e-3, r_w=0.53)
    '''
    
    :param Re: Reynolds number [-]
    :param epsilon: Pipe roughness [m]
    :param r_w: Pipe radius [m]
    :return f: friction coefficient [-]
    '''

    # pipe diameter
    d = 2*r_w
    # initial friction factor guess
    f = 0.1
    f_new = 0.0
    f_old

    while abs(f - f_new) < 1e-6:
        a = -2.0 * log((epsilon / d) / 3.7 + 2.51 / (Re * f_guess ** 0.5), 10)
        f_new = (1 / a) ** 2

    return


def pipe_dp(Q=1, r_f=100.0, r_w=0.25, k=100, mu=0.5, h=40.0, p_f=10.0, T=298.15, Z=1.0):
    """
    """

    rho
    mu

    # Q - radial flow rate[m3 / s]
    # P - pressure(f - formation edge, s - wellbore) [MPa]
    # R - radius(f - formation, w - wellbore)[m]
    # H - formation height[m]
    # K - permeability[mD]
    # Mu - viscosity[cP]
    # Z - gas deviation factor[-]

    delta_p = p_f - (p_f ** 2 - Q * mu * T * Z * log(r_f / r_w) / (8.834 * 10 ** -3 * k * h)) ** 0.5

    return delta_p
