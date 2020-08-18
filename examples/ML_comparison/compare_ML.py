from caes import ICAES

# ===========================
# common inputs
# ===========================
depth = 1402.35  # depth [m]
h = 62.44  # thickness [m]
phi = 0.2292  # porosity
k = 38.33  # permeability [mD]
m_dot = 200.0  # mass flow rate [kg/s]
r_f = 112.9995514  # formation radius [m]
r_w = 0.41 / 2.0  # well radius [m]

for i in range(2):

    inputs = ICAES.get_default_inputs()
    inputs['depth'] = depth
    inputs['h'] = h
    inputs['phi'] = phi
    inputs['k'] = k
    inputs['r_f'] = r_f
    inputs['r_w'] = r_w
    inputs['m_dot'] = m_dot

    # ===========================
    # ML = 1
    # ===========================
    if i == 0:
        casename = 'ML_one_'
        ML = 1.0
        inputs['ML_cmp1'] = ML
        inputs['ML_cmp2'] = ML
        inputs['ML_cmp3'] = ML

        inputs['ML_exp1'] = ML
        inputs['ML_exp2'] = ML
        inputs['ML_exp3'] = ML

    # ===========================
    # original ML
    # ===========================
    else:  # i == 1
        casename = 'ML_original_'
        inputs['ML_cmp1'] = 3.009
        inputs['ML_cmp2'] = 2.622
        inputs['ML_cmp3'] = 0.903

        inputs['ML_exp1'] = 0.963
        inputs['ML_exp2'] = 2.791
        inputs['ML_exp3'] = 3.188

    # ===========================
    # create system and run
    # ===========================
    system = ICAES(inputs=inputs)
    system.single_cycle()
    results = system.analyze_performance()
    print(results)
    results.to_csv(casename + 'single_cycle_performance.csv')
    system.data.to_csv(casename + 'single_cycle_timeseries.csv')
    # # plot results
    system.plot_overview(casename=casename)
    system.plot_pressures(casename=casename)
    system.plot_pressure_losses(casename=casename)
