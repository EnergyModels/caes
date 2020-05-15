from CoolProp.CoolProp import PropsSI
from scipy.interpolate import interp1d
from math import pi
import pandas as pd
import numpy as np
import math


def size_caes_trb(p_in=1.01325, t_in=400.0, t_out=20.0, p_out=1.01325, m_dot=2.2, RPM_low=10000, RPM_high=50000,
                 RPM_cases=5, piston=False, debug=False):
    if piston:
        # Sizing Rules
        PR_stg_min = 1.5
        PR_stg_max = 10.0

        # Specific Speed Chart Inputs
        Ns_ideal = np.array([])
        Ds_ideal = np.array([])
        eff_ideal = np.array([])

    else:  # radial/mixed/axial

        # Sizing Rules
        PR_stg_min = 1.5
        PR_stg_max = 3.6

        # Specific Speed Chart Inputs
        Ns_ideal = np.array([0.133572762, 0.212011551, 0.512807173, 0.654492961, 0.846899073, 1.025182722])
        Ds_ideal = np.array([10.09832427, 7.420479838, 3.489818315, 3.010946394, 2.563377933, 2.212805889])
        eff_ideal = np.array([0.7, 0.8, 0.9, 0.9, 0.8, 0.7])

    # Convert Inputs
    p_in = p_in * 1E5  # from bar to Pa
    t_in = t_in + 273.15  # from C to K
    t_out = t_out + 273.15  # from C to K
    p_out = p_out * 1E5  # from bar to Pa

    # Interpolate Specific Speed Chart Inputs
    f_Ds = interp1d(Ns_ideal, Ds_ideal)
    f_eff = interp1d(Ns_ideal, eff_ideal)

    # Determine range of stages to consider
    PR = p_in / p_out
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
    CP = PropsSI('CPMASS', "T", t_out, "P", p_out, fluid) / 1000.0  # KJ/Kg-K
    CV = PropsSI('CVMASS', "T", t_out, "P", p_out, fluid) / 1000.0  # KJ/Kg-K
    kappa = CP / CV
    MW = PropsSI('M', fluid) * 1000.0  # kg/kmol
    R_bar = PropsSI('GAS_CONSTANT', fluid)  # kJ/kmol/K
    R = R_bar / MW * 1000.0  # J/kg-K
    D3 = PropsSI('D', 'T', t_out, 'P', p_out, fluid)  # Density (kg/m3)
    V3 = m_dot * D3  # m3/s

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
        print('D3    :' + str(round(D3, 3)) + ' (kg/m^3)')
        print('V3    :' + str(round(V3, 3)) + ' (m^3/s)\n')
        print('Begin Cases')

    # DataFrame to hold results
    variables = ['p_in', 't_out', 'p_out', 'm_dot', 'V3', 'Nstg', 'PR_stg', 'RPM', 'H_ad',
                 'g', 'Ns', 'Ds', 'D', 'eff', 'type']
    df = pd.DataFrame(columns=variables)

    # Perform Runs
    for Nstg in Nstgs:

        PR_stg = PR ** (1.0 / Nstg)

        for RPM in RPMs:

            # Balje Calculations (Ideal gas)
            omega = 2 * pi / 60.0 * RPM  # rad/s
            # omega = RPM
            H_ad = kappa / (kappa - 1.0) * R * t_in * (1.0 - (1.0 / PR_stg) ** ((kappa - 1.0) / kappa))  # kJ/kg
            Ns = (omega * V3 ** 0.5) / H_ad ** 0.75

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
                D = (Ds * (V3) ** 0.5) / (g * H_ad) ** 0.25

                # Classify Machine Type
                if piston:
                    machine_type = 'Piston'
                else:
                    if Ns < Ns_radial[1]:
                        machine_type = 'Radial'
                    elif Ns_axial[0] < Ns:
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
                s = pd.Series(index=['Nstg', 'PR_stg', 'RPM', 'H_ad', 'g', 'Ns', 'Ds', 'D', 'eff', 'type'])
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
                df = df.append(s, ignore_index=True)

    # Store Inputs
    df.loc[:, 'p_in'] = p_in / 1E5  # from Pa back to bar
    df.loc[:, 't_out'] = t_out - 273.15  # from K back to C
    df.loc[:, 'p_out'] = p_out / 1E5  # from Pa back to bar
    df.loc[:, 'm_dot'] = m_dot  # kg/s
    df.loc[:, 'V3'] = V3  # m3/s

    return df
