from math import pi, exp, log


def pipe_heat_transfer_subsurface(r_pipe=0.205, t_pipe=0.01, t_cement=0.0347, r_rock=10.0, depth=1402.35,
                                  Tm=325.0, Ts=295.0, m_dot=325.0,
                                  k_pipe=56.7, k_cement=0.72, k_rock=2.90, k_air=0.033242,
                                  rho=169.11, mu=21.492e-6, Pr=0.79960, cp=1236.8,
                                  debug=False):
    """
    Assumes constant density
    :param r_pipe: pipe radius [m]
    :param t_pipe: pipe wall thickness [m]
    :param t_cement: concrete thickness [m]
    :param r_rock: distance to "infinity" where formation temperature, Ts, is fixed [m]
    :param depth: well depth / pipe length [m]

    :param Tm: air temperature entering pipe [K]
    :param Ts: formation fixed temperature [K]
    :param m_dot: mass flow [kg/s]

    :param k_pipe: thermal conductivity of pipe [W/m-K], default Incropera Table A.1 for Carbon Steel p 930
    :param k_cement: thermal conductivity of cement [W/m-K], default Incropera Table A.3 for Cement mortar p 935
    :param k_rock: thermal conductivity of rock/formation [W/m-K], default Incropera Table A.3 for Sandstone,Berea p 940

    properties of air (defaults taken from air at 14 MPa, 290 K in REFPROP
    :param k_air: thermal conductivity of air [W/m-K]
    :param rho: air density [kg/m^3]
    :param mu: air viscosity [Pa*s]
    :param Pr: air Prandtl number [-]
    :param cp: air heat capacity [J/kg-K]

    :param debug: debug option [Boolean]

    :return delta_T: temperature change [K]
    """

    # Reynolds number
    A = pi / 4.0 * (r_pipe * 2.0) ** 2.0  # pipe cross-sectional area [m^2]
    U = m_dot / (rho * A)  # velocity [m/s]
    Re = rho * (r_pipe * 2.0) * abs(U) / mu  # [-]

    # Nusselt Number
    if Ts > Tm:  # heating
        n = 0.4
    else:  # cooling
        n = 0.3
    Nu = 0.023 * Re ** (4.0 / 5.0) * Pr ** n  # [-]

    # Heat transfer coefficient
    h = Nu * k_air / (2 * r_pipe)  # [W/m^2*K]

    # thermal resistance
    r1 = r_pipe
    r2 = r_pipe + t_pipe
    r3 = r_pipe + t_pipe + t_cement
    r4 = r_pipe + t_pipe + t_cement + r_rock
    R_pipe_conv = 1 / (2 * pi * r1 * depth * h)
    R_pipe_cond = log(r2 / r1) / (2 * pi * depth * k_pipe)
    R_cement_cond = log(r3 / r2) / (2 * pi * depth * k_cement)
    R_rock_cond = log(r4 / r3) / (2 * pi * depth * k_rock)
    R_tot = R_pipe_conv + R_pipe_cond + R_cement_cond + R_rock_cond
    UA = 1 / R_tot

    # heat transfer
    Tm_out = Ts - (Ts - Tm) * exp(-UA / (abs(m_dot) * cp))
    delta_T = Tm - Tm_out

    if debug:
        print('Re      [-] :' + str(Re))
        print('Nu      [-] :' + str(Nu))
        print('h  [W/m^-K] :' + str(h))
        print('R_pipe_conv  [W/m^-K] :' + str(R_pipe_conv))
        print('R_pipe_cond  [W/m^-K] :' + str(R_pipe_cond))
        print('R_cement_cond  [W/m^-K] :' + str(R_cement_cond))
        print('R_rock_cond  [W/m^-K] :' + str(R_rock_cond))
        print('R_tot  [W/m^-K] :' + str(R_tot))
        print('UA  [W/m^-K] :' + str(UA))
        print('Ts      [K] :' + str(Ts))
        print('Tm_in   [K] :' + str(Tm))
        print('Tm_out  [K] :' + str(Tm_out))
        print('delta_T [K] :' + str(delta_T))

    return delta_T


def pipe_heat_transfer_ocean(r_pipe=0.205, depth=25.0, t_pipe=0.01, t_insul=0.02,
                             Tm=325.0, Ts=290.0, m_dot=325.0,
                             k_pipe=56.7, k_air=0.033242, k_insul=0.46,
                             rho=169.11, mu=21.492e-6, Pr=0.79960, cp=1236.8,
                             h_ocean=3000,
                             debug=False):
    """
    Assumes constant density
    :param r_pipe: pipe radius [m]
    :param depth: pipe length exposed to ocean [m]
    :param t_pipe: pipe wall thickness [m]
    :param t_insul: insulation thickness [m]

    :param Tm: air temperature entering pipe [K]
    :param Ts: ocean fixed temperature [K]
    :param m_dot: mass flow [kg/s]


    :param k_insul: thermal conductivity of insulation (just through ocean) [W/m-K], from Li 2017
    :param k_pipe: thermal conductivity of pipe [W/m-K], default Incropera Table A.1 for Carbon Steel p 930

    properties of air (defaults taken from air at 14 MPa, 290 K in REFPROP
    :param k_air: thermal conductivity of air [W/m-K]
    :param rho: air density [kg/m^3]
    :param mu: air viscosity [Pa*s]
    :param Pr: air Prandtl number [-]
    :param cp: air heat capacity [J/kg-K]

    :param h_ocean: free convection of ocean water (W/m^2-K), Engineering Toolbox upper limit

    :param debug: debug option [Boolean]

    :return delta_T: temperature change [K]
    """

    # Reynolds number
    A = pi / 4.0 * (r_pipe * 2.0) ** 2.0  # pipe cross-sectional area [m^2]
    U = m_dot / (rho * A)  # velocity [m/s]
    Re = rho * (r_pipe * 2.0) * abs(U) / mu  # [-]

    # Nusselt Number
    if Ts > Tm:  # heating
        n = 0.4
    else:  # cooling
        n = 0.3
    Nu = 0.023 * Re ** (4.0 / 5.0) * Pr ** n  # [-]

    # Heat transfer coefficient inside pipe
    h = Nu * k_air / (2 * r_pipe)  # [W/m^2*K]

    # thermal resistance
    r1 = r_pipe
    r2 = r_pipe + t_pipe
    r3 = r_pipe + t_pipe + t_insul
    R_pipe_conv = 1 / (2 * pi * r1 * depth * h)
    R_pipe_cond = log(r2 / r1) / (2 * pi * depth * k_pipe)
    R_insul_cond = log(r3 / r2) / (2 * pi * depth * k_insul)
    R_ocean_conv = 1 / (2 * pi * r3 * depth * h_ocean)
    R_tot = R_pipe_conv + R_pipe_cond + R_insul_cond + R_ocean_conv
    UA = 1 / R_tot

    # heat transfer
    Tm_out = Ts - (Ts - Tm) * exp(-UA / (abs(m_dot) * cp))
    delta_T = Tm - Tm_out

    if debug:
        print('Re      [-] :' + str(Re))
        print('Nu      [-] :' + str(Nu))
        print('h  [W/m^-K] :' + str(h))
        print('R_pipe_conv  [W/m^-K] :' + str(R_pipe_conv))
        print('R_pipe_cond  [W/m^-K] :' + str(R_pipe_cond))
        print('R_insul_cond  [W/m^-K] :' + str(R_insul_cond))
        print('R_ocean_conv  [W/m^-K] :' + str(R_ocean_conv))
        print('R_tot  [W/m^-K] :' + str(R_tot))
        print('UA  [W/m^-K] :' + str(UA))
        print('Ts      [K] :' + str(Ts))
        print('Tm_in   [K] :' + str(Tm))
        print('Tm_out  [K] :' + str(Tm_out))
        print('delta_T [K] :' + str(delta_T))

    return delta_T
