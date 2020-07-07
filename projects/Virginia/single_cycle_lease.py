from caes import ICAES, plot_series
import matplotlib.pyplot as plt
from math import pi

# lease parameters
depth = 1402.35  # depth [m]
h = 62.44  # thickness [m]
phi = 0.2292  # porosity
k = 38.67  # permeability [mD]
length = 12.0 * 1609.34  # convert miles to m
width = 15.0 * 1609.34
fr_formation = 0.5  # fraction of lease covering formation
m_dot = 200  # mass flow rate [kg/s]

# calculate equivalent radius (aquifer shape assumed to be circular)
area = length * width * fr_formation
r_f = (area / pi) ** 0.5

# create system
inputs = ICAES.get_default_inputs()
inputs['depth'] = depth
inputs['h'] = h
inputs['phi'] = phi
inputs['k'] = k
inputs['r_f'] = r_f
system = ICAES(inputs=inputs)

# run single cycle and analyze
system.single_cycle(m_dot=m_dot)
results = system.analyze_performance()
results.to_csv('single_cycle_performance.csv')
system.data.to_csv('single_cycle_timeseries.csv')
print(results)

# # plot results
system.plot_overview()
system.plot_pressures()
system.plot_pressure_losses()
