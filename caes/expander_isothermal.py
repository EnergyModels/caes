import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function


def isothermal_exp(ML, T_air_in, p_air_in, p_air_out, T_water_in, p_water_in, eta_pump):
    """
        Simulates a near-isothermal expander

        Parameters:
            ML- mass loading ratio [-]
            T_air_in [K]
            p_air_in [Pa]
            p_air_out [Pa]
            T_water_in [K]
            p_water_in [Pa] - pressure of water before it is pumped into spray nozzle

        Returns:
            T_air_out [K]
            w_total [J/kg] - per kg of air
            w_cmp [J/kg] - per kg of air
            w_pmp [J/kg] - per kg of air
        """

    air = 'AIR.MIX'
    water = 'Water'

    # air inlet properties
    cp = CP.PropsSI('CPMASS', 'T', T_air_in, 'P', p_air_in, air)  # constant pressure specific heat [J/kg-K]
    cv = CP.PropsSI('CVMASS', 'T', T_air_in, 'P', p_air_in, air)  # constrant volume specific heat [J/kg-K]
    k = cp / cv  # heat capacity ratio [-]
    R = CP.PropsSI('GAS_CONSTANT', air)  # Ideal gas constant [J/mol-K]
    M = CP.PropsSI('M', air)  # Ideal gas constant [kg/mol]

    # water inlet properties
    cd = CP.PropsSI('CPMASS', 'T', T_water_in, 'P', p_water_in, water)  # constant pressure specific heat [J/kg-K]
    v_water = 1.0 / CP.PropsSI('D', 'T', T_water_in, 'P', p_water_in, water)  # specific volume(1/density) [m3/kg]

    # polytropic exponent
    n = k * (1 + ML * (cd / cp)) / (1 + k * ML * (cd / cp))  # [-]

    # air outlet properties
    T_air_out = T_air_in * (p_air_out / p_air_in) ** ((n - 1.0) / n)

    # expander work
    # w_exp = n * R * T_air_in / (n - 1) * (1 - (p_air_out / p_air_in) * ((n - 1) / n))  # [J/kg]
    w_exp = R / M * (T_air_out - T_air_in) / (1.0 - n)

    # pump work [J/kg]
    w_pmp = - ML * v_water * (p_air_in - p_water_in) / eta_pump

    # total work
    w_total = w_exp + w_pmp

    return T_air_out, w_total, w_exp, w_pmp, n
