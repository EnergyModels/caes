import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from caes import isothermal_cmp

# Compressor test
T_air_in = 273.15 + 25.0  # [K]
p_air_in = 101325.0  # [Pa]
T_water_in = 273.15 + 25.0  # [K]
p_water_in = 101325.0  # [Pa]
eta_pump = 0.75  # [Fr] Pump efficiency

# Pressure ratios
PRs = np.arange(1.1, 5.1, 0.1)  # pressure ratios
MLs = np.arange(0.5, 2.0, 0.25)  # mass loading ratios

# Store results
entries = ['ML', 'PR', 'p_air_out', 'T_air_out', 'w_total', 'w_cmp', 'w_pmp']
df = pd.DataFrame(columns=entries)

for PR in PRs:
    for ML in MLs:
        # compute outlet pressure
        p_air_out = p_air_in * PR

        # compute performance
        T_air_out, w_total, w_cmp, w_pmp = isothermal_cmp(ML, T_air_in, p_air_in, p_air_out, T_water_in, p_water_in,
                                                          eta_pump)
        # store results
        s = pd.Series(index=entries, dtype='float64')
        s['ML'] = ML
        s['PR'] = PR
        s['p_air_out'] = p_air_out
        s['T_air_out'] = T_air_out
        s['w_total'] = w_total
        s['w_cmp'] = w_cmp
        s['w_pmp'] = w_pmp
        df = df.append(s, ignore_index=True)

# plot results
# a = plt.subplot(4, 1)
# sns.set_style('white')
# sns.lineplot(data=df, x='PR', y='T_air_out', hue='ML', ax=a[0], palette='colorblind')
# sns.lineplot(data=df, x='PR', y='w_total', hue='ML', ax=a[1], palette='colorblind', legend=False)
# sns.lineplot(data=df, x='PR', y='w_cmp', hue='ML', ax=a[2], palette='colorblind', legend=False)
# sns.lineplot(data=df, x='PR', y='w_pmp', hue='ML', ax=a[3], palette='colorblind', legend=False)


x_var = 'PR'
x_label = 'Pressure ratio [-]'
y_vars = ["T_air_out", "w_total", "w_cmp", "w_cmp"]
y_labels = ["Outlet Temp\n[K]", "Total work\n[J/kg-air]", "Compression work\n[J/kg-air]", "Pump work\n[J/kg-air]"]
y_converts = [1.0, 1.0, 1.0, 1.0]

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 5.5  # inches

# Create plot
f, a = plt.subplots(4, 1, sharex='col')

# Set size
f.set_size_inches(width, height)

colors = sns.color_palette('colorblind')

for i, (y_var, y_label, y_convert) in enumerate(zip(y_vars, y_labels, y_converts)):
    ax = a[i]

    for j, ML in enumerate(MLs):
        color = colors[j]
        df2 = df[(df.loc[:, 'ML'] == ML)]
        x = list(df2.loc[:, x_var])
        y = list(df2.loc[:, y_var])
        ax.plot(x, y, markeredgecolor=color, markerfacecolor=color)

    # Labels
    if i == 3:
        ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

# legend
patches = []
for j, ML in enumerate(MLs):
    patches.append(mpatches.Patch(color=colors[j], label=str(ML)))
leg = ax.legend(handles=patches, bbox_to_anchor=(0.5, -0.25), loc="upper center", title="Mass Loading Ratio", ncol=3)
plt.tight_layout()
plt.subplots_adjust(wspace=0.2)
plt.savefig('isothermal_cmp.png', DPI=600, bbox_extra_artists=leg)
