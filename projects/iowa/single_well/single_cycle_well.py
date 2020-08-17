from caes import ICAES
from math import pi

# well parameters
depth = 573.0  # [m] 1880 ft
h = 20.6  # [m] 65-70 ft
phi = 0.165  # [-] average of 16 and 17
k = 3.0  # permeability [mD] - to accentuate pressure drop
m_dot = 24.0  # mass flow rate [kg/s]
r_f = 200.0  # formation radius [m]

# create system
inputs = ICAES.get_default_inputs()
inputs['depth'] = depth
inputs['h'] = h
inputs['phi'] = phi
inputs['k'] = k
inputs['r_f'] = r_f
inputs['m_dot'] = m_dot

inputs['p_frac_grad'] = 20.0
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
