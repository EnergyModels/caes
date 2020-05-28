from math import log, pi


def sopher_method(Q=1, r_f=100.0, r_w=0.25, k=100, mu=0.5, h=40.0, p_f=10.0, T=298.15, Z=1.0):
    """
    """

    # Q - radial flow rate[m3 / s]
    # P - pressure(f - formation edge, s - wellbore) [MPa]
    # R - radius(f - formation, w - wellbore)[m]
    # H - formation height[m]
    # K - permeability[mD]
    # Mu - viscosity[cP]
    # Z - gas deviation factor[-]

    delta_p = (p_f ** 2 + Q * mu * T * Z * log(r_f / r_w) / (8.834 * 10 ** -3 * k * h)) ** 0.5 - p_f

    return delta_p


def confined_flow(Q=1, r_f=100.0, r_w=0.25, k=100, mu=250.0, h=40.0, ):
    """
    inputs:
    Q - radial flow rate [m3 / s]
    r_f - formation radius [m]
    r_w - wellbore radius [m]
    k - permeability[mD]
    mu - viscosity[cP]
    h - formation height[m]

    output:
    delta_p - pressure drop [MPa]
    """

    # conversions
    mu = mu * 0.001  # convert cP to Pa*s https://www.unitconverters.net/viscosity-dynamic/centipoise-to-pascal-second.htm
    k = k * 0.001  # convert from mD to D https://www.shell.com.au/about-us/projects-and-locations/qgc/environment/water-management/water-monitoring-and-measurement/_jcr_content/par/textimage_7fad.stream/1494308815573/b047250c96f6e182fd4478c56b83751f15363209/water-map-glossary.pdf
    k = k * 9.869223e-13  # convert D to m^2 https://www.calculator.org/properties/permeability.html

    # calculate
    delta_p = Q * mu * log(r_f / r_w) / (2 * pi * k * h)

    # convert result to MPa
    delta_p = delta_p * 1e-6

    return delta_p


def unconfined_flow(Q=1, r_f=100.0, r_w=0.25, k=100, mu=250.0, p_f=10.0, rho=40.0):
    """
    input:
    Q - radial flow rate[m3/ s]
    r_f - formation radius [m]
    r_w - wellbore radius [m]
    k - permeability [mD]
    mu - viscosity[cP]
    p_f - formation pressure [MPa]
    rho - [kg/m^3]

    output:
    delta_p - pressure drop [MPa]
    """
    # constant
    g = 9.81  # [m/s^2]

    # conversions
    mu = mu * 0.001  # convert cP to Pa*s https://www.unitconverters.net/viscosity-dynamic/centipoise-to-pascal-second.htm
    k = k * 0.001  # convert from mD to D https://www.shell.com.au/about-us/projects-and-locations/qgc/environment/water-management/water-monitoring-and-measurement/_jcr_content/par/textimage_7fad.stream/1494308815573/b047250c96f6e182fd4478c56b83751f15363209/water-map-glossary.pdf
    k = k * 9.869223e-13  # convert D to m^2 https://www.calculator.org/properties/permeability.html
    p_f = p_f * 1e6 # convert from MPa to Pa

    # calculate
    delta_p = (p_f ** 2 + Q * mu * rho * g * log(r_f / r_w) / (pi * k)) ** 0.5 - p_f

    # convert result to MPa (from Pa)
    delta_p = delta_p * 1e-6

    return delta_p
