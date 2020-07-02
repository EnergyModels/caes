from caes import ICAES, plot_series
import matplotlib.pyplot as plt

# create system
inputs = ICAES.get_default_inputs()
system = ICAES(inputs=inputs)

# system.debug_perf()
#
# # run single cycle and analyze
system.single_cycle()
results = system.analyze_performance()
results.to_csv('single_cycle_performance.csv')
system.data.to_csv('single_cycle_timeseries.csv')
print(results)

# # plot results
system.plot_overview()
system.plot_pressures()
system.plot_pressure_losses()
