from caes import ICAES
from math import pi

# well parameters
depth = 1402.35  # depth [m]
h = 62.44  # thickness [m]
phi = 0.2292  # porosity
k = 38.67  # permeability [mD]
m_dot = 100.0  # mass flow rate [kg/s]
r_f = 200.0  # formation radius [m]

# create system
inputs = ICAES.get_default_inputs()
inputs['depth'] = depth
inputs['h'] = h
inputs['phi'] = phi
inputs['k'] = k
inputs['r_f'] = r_f
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
