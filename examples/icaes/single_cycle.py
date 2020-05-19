from caes import ICAES, plot_series
import matplotlib.pyplot as plt

# create system
inputs = ICAES.get_default_inputs()
inputs['p_store_min'] = 10.0e3  # kPa
inputs['p_store_init'] = 10.0e3  # kPa
inputs['p_store_max'] = 22.0e3  # kPa
system = ICAES(inputs=inputs)

# run single cycle and analyze
system.single_cycle()
results = system.analyze_performance()
results.to_csv('single_cycle_performance.csv')
system.data.to_csv('single_cycle_timeseries.csv')
print(results)

# ==============
# plot results
# ==============
df = system.data
df.loc[:, 'step'] = df.index

x_var = 'step'
x_label = 'Step [-]'
x_convert = 1.0

y_vars = ['m_store', 'p_store', 'total_work_per_kg', 'pwr']
y_labels = ['Air stored\n[kton]', 'Well pressure\n[MPa]', 'Work\n[kJ/kg]', 'Power\n[MW]']
y_converts = [1.0e-6, 1.0e-3, 1.0, 1.0e-3]

plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts)
plt.savefig('single_cycle.png', dpi=600)
plt.close()
