from caes import ICAES2
from math import pi

# well parameters
depth = 1123.16  # [m]
h = 297.50  # [m]
phi = 0.2820  # [-]
k = 236.1424  # [mD]
capacity = 200  # [MW]
duration = 24  # [hr]
r_w = 0.41 / 2.0  # [m]
m_dot = 619.960576753886  # mass flow rate [kg/s]
r_f = 127.023986376374  # formation radius [m]

# create system
inputs = ICAES2.get_default_inputs()
inputs['depth'] = depth
inputs['h'] = h
inputs['phi'] = phi
inputs['k'] = k
inputs['r_f'] = r_f
inputs['r_w'] = r_w
inputs['m_dot'] = m_dot

system = ICAES2(inputs=inputs)

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