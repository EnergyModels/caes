from caes import CAES

# create system
inputs = CAES.get_default_inputs()
system = CAES(inputs=inputs)

# run single cycle and analyze
system.single_cycle()
results = system.analyze_performance()
results.to_csv('single_cycle_performance.csv')
system.data.to_csv('single_cycle_timeseries.csv')
print(results)

# plot results
system.plot_overview()
system.plot_pressures()
system.plot_pressure_losses()
