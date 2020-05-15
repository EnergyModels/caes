from CoolProp.CoolProp import PropsSI
from scipy.interpolate import interp1d
from math import pi
import pandas as pd
import numpy as np
import math


# Specific Speed Chart Inputs
def size_caes_cmp(p_in=1.01325, t_in=20.0, p_out=10.0, m_dot=2.2, RPM_low=10000, RPM_high=50000, RPM_cases=5,
                  machine_type='radial-mixed-axial', debug=False):
    Ns_conversion = 2 * math.pi / 60.0 / (
            32.2 ** 0.5)  # converts between Balje specific speed maps and Barber-nichols maps
    Ds_conversion = (32.2) ** 0.25
    # Barber-nichols maps: https://barber-nichols.com/media/tools-resources/
    # Balje: Balje, O.E., “Turbomachines”, John Wiley & Sons, 1981

    if machine_type == 'piston':
        # Sizing Rules
        PR_stg_min = 1.5
        PR_stg_max = 10.0
        # Specific Speed Chart Inputs
        Ns_ideal = Ns_conversion * np.array(
            [0.002872329, 0.00590389, 0.008295814, 0.014572054, 0.035995733, 0.10316148, 0.300691974, 0.608738487,
             1.01146603, 1.617291568, 2.25500884])
        Ds_ideal = Ds_conversion * np.array(
            [31.41541905, 24.14666422, 20.08432049, 16.48704628, 12.50670359, 10.2323066, 7.77903859, 6.237728314,
             5.078561789, 3.92018785, 2.980295035])
        eff_ideal = np.array([0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, ])

    elif machine_type == 'rotary-piston':
        # Sizing Rules
        PR_stg_min = 1.5
        PR_stg_max = 10.0
        # Specific Speed Chart Inputs
        Ns_ideal = Ns_conversion * np.array(
            [2.109891057, 2.57455404, 3.267744356, 4.425670872, 5.998756468, 10.18117455, 28.15197286, 65.54821372,
             127.0142239, 143.1603893, 174.6004778])
        Ds_ideal = Ds_conversion * np.array(
            [2.485830474, 2.519073184, 2.420655319, 1.931324482, 1.713687991, 1.404082411, 0.814427152, 0.504845249,
             0.408178234, 0.424773753, 0.402791749])
        eff_ideal = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 0.7, 0.6, 0.5])

    elif machine_type == 'radial-mixed-axial':  # radial/mixed/axial
        # Sizing Rules
        PR_stg_min = 1.5
        PR_stg_max = 3.6
        # Specific Speed Chart Inputs
        Ns_ideal = Ns_conversion * np.array(
            [17.08552039, 20.11489472, 23.24840648, 29.15502332, 39.30029828, 59.07563978, 337.6362693, 824.9591252,
             1925.245424, 3710.761211])
        Ds_ideal = Ds_conversion * np.array(
            [8.007409952, 7.045900533, 6.032206364, 4.844378804, 3.51843236, 2.397080062, 0.800740995, 0.737526752,
             0.654923352, 0.603220636])
        eff_ideal = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8, 0.7, 0.6, 0.5])

        # for classification
        Ns_radial = Ns_conversion * 59.07563978  # less than this is radial
        Ns_axial = Ns_conversion * 337.6362693  # more than this is axial, remainer is mixed

    else:
        print('machine type must be equal to ''piston'', ''rotary-piston'', or ''radial-mixed-axial''')
        return

    # Convert Inputs
    p_in = p_in * 1E5  # from bar to Pa
    t_in = t_in + 273.15  # from C to K
    p_out = p_out * 1E5  # from bar to Pa

    # Interpolate Specific Speed Chart Inputs
    f_Ds = interp1d(Ns_ideal, Ds_ideal)
    f_eff = interp1d(Ns_ideal, eff_ideal)

    # Determine range of stages to consider
    PR = p_out / p_in
    Nstg_low = math.ceil(math.log(PR) / math.log(PR_stg_max))
    Nstg_high = math.floor(math.log(PR) / math.log(PR_stg_min))
    Nstgs = np.arange(Nstg_low, Nstg_high, 1)
    if len(Nstgs) == 0:
        Nstgs = [Nstg_low]
    if debug:
        print('Range of Stages Considered')
        print('Nstg_low  :' + str(round(Nstg_low, 0)))
        print('Nstg_high :' + str(round(Nstg_high, 0)))
        print('Nstgs     :' + str(Nstgs) + '\n')

    # RPMs to consider
    RPMs = np.linspace(RPM_low, RPM_high, RPM_cases)

    # Constants and Fluid Properties
    g = 9.81  # m/s^2
    fluid = 'Air'
    CP = PropsSI('CPMASS', "T", t_in, "P", p_in, fluid) / 1000.0  # KJ/Kg-K
    CV = PropsSI('CVMASS', "T", t_in, "P", p_in, fluid) / 1000.0  # KJ/Kg-K
    kappa = CP / CV
    MW = PropsSI('M', fluid) * 1000.0  # kg/kmol
    R_bar = PropsSI('GAS_CONSTANT', fluid)  # kJ/kmol/K
    R = R_bar / MW * 1000.0  # J/kg-K
    D1 = PropsSI('D', 'T', t_in, 'P', p_in, fluid)  # Density (kg/m3)
    V1 = m_dot * D1  # m3/s

    # Print-out values, if debugging
    if debug:
        print('Constants and Fluid Properties:')
        print('g     :' + str(round(g, 3)) + ' (m/s^2)')
        print('CP    :' + str(round(CP, 3)) + ' (kJ/kg-K)')
        print('CV    :' + str(round(CV, 3)) + ' (kJ/kg-K)')
        print('kappa :' + str(round(kappa, 3)) + ' (-)')
        print('MW    :' + str(round(MW, 3)) + ' (kg/kmol)')
        print('R_bar :' + str(round(R_bar, 3)) + ' (kJ/kmol-K)')
        print('R     :' + str(round(R, 3)) + ' (J/kg-K)')
        print('D1    :' + str(round(D1, 3)) + ' (kg/m^3)')
        print('V1    :' + str(round(V1, 3)) + ' (m^3/s)\n')
        print('Begin Cases')

    # DataFrame to hold results
    variables = ['p_in', 't_in', 'p_out', 'm_dot', 'V1', 'Nstg', 'PR_stg', 'RPM', 'H_ad',
                 'g', 'Ns', 'Ds', 'D', 'eff', 'type', 'r1', 'r2', 'U2', 'psi', 'I', 'mu']
    df = pd.DataFrame(columns=variables)

    # Perform Runs
    for Nstg in Nstgs:

        PR_stg = PR ** (1.0 / Nstg)

        for RPM in RPMs:

            # Balje Calculations (Ideal gas)
            omega = 2 * pi / 60.0 * RPM  # rad/s
            # omega = RPM
            H_ad = kappa / (kappa - 1.0) * R * t_in * (PR ** ((kappa - 1.0) / kappa) - 1.0) / Nstg  # kJ/kg
            Ns = (omega * V1 ** 0.5) / H_ad ** 0.75

            # Print-out values, if debugging
            if debug:
                print('Nstg  :' + str(round(Nstg, 0)) + ' (-)')
                print('PR_stg:' + str(round(PR_stg, 2)) + ' (-)')
                print('RPM   :' + str(round(RPM, 0)) + ' (rev/min)')
                print('omega :' + str(round(omega, 2)) + ' (rad/s)')
                print('H_ad  :' + str(round(H_ad, 2)) + ' (kJ/kg)')
                print('Ns    :' + str(round(Ns, 3)) + " (-)\n")

            # Check if within the interpolation limits
            if Ns_ideal.min() <= Ns <= Ns_ideal.max():
                eff = f_eff(Ns)
                Ds = f_Ds(Ns)
                D = (Ds * V1 ** 0.5) / (g * H_ad) ** 0.25

                r2 = D / 2.0  # Tip radius (m)
                r1 = r2 / 2.0  # Hub radius (m)
                U2 = omega * r2  # Tip speed (m/s)
                psi = V1 / (math.pi * r2 ** 2.0 * U2)  # Flow coefficient (-)
                I = H_ad / U2 ** 2.0  # Work input coefficient (-)
                mu = eff * I  # Work coefficient (-)

                # Classify Machine Type
                if machine_type == 'piston':
                    machine_type = 'Piston'
                elif machine_type == 'rotary-piston':
                    machine_type = 'Rotary Piston'
                elif machine_type == 'radial-mixed-axial':
                    if Ns < Ns_radial:
                        machine_type = 'Radial'
                    elif Ns_axial < Ns:
                        machine_type = 'Axial'
                    else:
                        machine_type = 'Mixed'

                # Print-out values, if debugging
                if debug:
                    print("Successfully sized")
                    print('Ds    :' + str(round(Ds, 3)))
                    print('D     :' + str(round(D, 3)))
                    print('eff   :' + str(round(eff, 3)))
                    print('#================#\n')

                # Save Values
                s = pd.Series(index=['Nstg', 'PR_stg', 'RPM', 'H_ad', 'g', 'Ns', 'Ds', 'D', 'eff', 'type',
                                     'r1', 'r2', 'U2', 'psi', 'I', 'mu'])
                s['Nstg'] = Nstg
                s['PR_stg'] = PR_stg
                s['RPM'] = RPM
                s['H_ad'] = H_ad
                s['g'] = g
                s['Ns'] = Ns
                s['Ds'] = Ds
                s['D'] = D
                s['eff'] = eff
                s['type'] = machine_type
                s['r1'] = r1
                s['r2'] = r2
                s['U2'] = U2
                s['psi'] = psi
                s['I'] = I
                s['mu'] = mu
                df = df.append(s, ignore_index=True)

    # Store Inputs
    df.loc[:, 'p_in'] = p_in / 1E5  # from Pa back to bar
    df.loc[:, 't_in'] = t_in - 273.15  # from K back to C
    df.loc[:, 'p_out'] = p_out / 1E5  # from Pa back to bar
    df.loc[:, 'm_dot'] = m_dot  # kg/s
    df.loc[:, 'V1'] = V1  # m3/s

    return df
