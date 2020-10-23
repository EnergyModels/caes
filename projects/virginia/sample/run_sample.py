from caes import ICAES
from math import pi

# well parameters
depth = 1402.35  # [m]
h = 62.44  # [m]
phi = 0.2292  # [-]
k = 38.33  # [mD]
capacity = 100  # [MW]
duration = 24  # [hr]
r_w = 0.41/2.0  # [m]
m_dot = 562.1754469  # mass flow rate [kg/s]
r_f = 180.3740783  # formation radius [m]

# create system
inputs = ICAES.get_default_inputs()
inputs['depth'] = depth
inputs['h'] = h
inputs['phi'] = phi
inputs['k'] = k
inputs['r_f'] = r_f
inputs['r_w'] = r_w
inputs['m_dot'] = m_dot

system = ICAES(inputs=inputs)

# run single cycle and analyze
system.single_cycle()
results = system.analyze_performance()
results.to_csv('single_cycle_performance.csv')
system.data.to_csv('single_cycle_timeseries.csv')
print(results)

# # plot results
system.plot_overview()
system.plot_pressures()
system.plot_pressure_losses()

# print working pressure range
print(system.p_store_min)
print(system.p_store_max)