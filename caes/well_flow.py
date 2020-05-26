from math import log


def sopher_method(Q=1, p_f=10.0, r_f=100.0, r_w=0.5, k=100, h=40.0, mu=0.5, T=298.15, Z=1.0):


    """
    """

    # Q - radial flow rate[m3 / s]
    # P - pressure(f - formation edge, s - wellbore) [MPa]
    # R - radius(f - formation, w - wellbore)[m]
    # H - formation height[m]
    # K - permeability[mD]
    # Mu - viscosity[cP]
    # Z - gas deviation factor[-]

    p_s = (p_f**2 - Q * mu * T * Z * log(r_f / r_w) / (8.834 * 10 ** -3 * k * h))**0.5
    delta_p = p_f - p_s

    return delta_p
