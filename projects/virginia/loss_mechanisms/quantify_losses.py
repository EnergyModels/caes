from caes import CAES, ICAES
import pandas as pd


# well parameters
depth = 1402.35  # depth [m]
h = 62.44  # thickness [m]
phi = 0.2292  # porosity
k = 38.33  # permeability [mD]
m_dot = 565.0428614  # mass flow rate [kg/s]
r_f = 180.3177957  # formation radius [m]
r_w = 0.41 / 2.0  # well radius [m]

df = pd.DataFrame()

for i in range(9):

    # get default inputs
    if i == 0:
        inputs = CAES.get_default_inputs()
    else:
        inputs = ICAES.get_default_inputs()

    # Common inputs
    inputs['depth'] = depth
    inputs['h'] = h
    inputs['phi'] = phi
    inputs['k'] = k
    inputs['r_f'] = r_f
    inputs['r_w'] = r_w
    inputs['m_dot'] = m_dot

    # options to include/exclude various loss mechanisms
    inputs['include_interstage_dp'] = False
    inputs['include_thermal_gradient'] = True
    inputs['include_air_leakage'] = False
    inputs['include_aquifer_dp'] = False
    inputs['include_pipe_dp_gravity'] = False
    inputs['include_pipe_dp_friction'] = False
    inputs['include_pipe_heat_transfer'] = False
    if i >= 2:
        inputs['include_interstage_dp'] = True
    if i >= 3:
        inputs['include_thermal_gradient'] = True
    if i >= 4:
        inputs['include_air_leakage'] = True
    if i >= 5:
        inputs['include_aquifer_dp'] = True
    if i >= 6:
        inputs['include_pipe_dp_gravity'] = True
    if i >= 7:
        inputs['include_pipe_dp_friction'] = True
    if i >= 8:
        inputs['include_pipe_heat_transfer'] = True

    # create system
    if i == 0:
        system = CAES(inputs=inputs)
    else:
        system = ICAES(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle()
    results = system.analyze_performance()

    # save results
    # results = results.append(inputs, ignore_index=True)
    df = df.append(results, ignore_index=True)

    # save time series data
    savename = 'single_cycle_timeseries_' + str(i) + '.csv'
    system.data.to_csv(savename)

# save to csv
df.to_csv('loss_results.csv')

# isothermal
# near-isothermal
# machine pressure losses
# thermal gradient
# air leakage
# aquifer losses
# gravity potential
# pipe friction
# pipe heat transfer
