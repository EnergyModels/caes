import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from caes import isothermal_exp

# Expander test
T_air_in = 273.15 + 25.0  # [K]
p_air_out = 101325.0  # [Pa]
T_water_in = 273.15 + 25.0  # [K]
p_water_in = 101325.0  # [Pa]
eta_pump = 0.75  # [Fr] Pump efficiency

# Parameters to test
PRs = np.arange(1.1, 5.1, 0.1)  # pressure ratios
MLs = np.arange(0.5, 2.25, 0.25)  # mass loading ratios

# Store results
entries = ['ML', 'PR', 'p_air_in', 'T_air_in', 'p_air_out', 'T_air_out', 'w_total', 'w_exp', 'w_pmp', 'n']
df = pd.DataFrame(columns=entries)

for PR in PRs:
    for ML in MLs:
        # compute outlet pressure
        p_air_in = p_air_out * PR

        # compute performance
        T_air_out, w_total, w_exp, w_pmp, n = isothermal_exp(ML, T_air_in, p_air_in, p_air_out, T_water_in, p_water_in,
                                                             eta_pump)
        # store results
        s = pd.Series(index=entries, dtype='float64')
        s['ML'] = ML
        s['PR'] = PR
        s['p_air_in'] = p_air_in
        s['T_air_in'] = T_air_in
        s['p_air_out'] = p_air_out
        s['T_air_out'] = T_air_out
        s['w_total'] = w_total
        s['w_exp'] = w_exp
        s['w_pmp'] = w_pmp
        s['n'] = n
        df = df.append(s, ignore_index=True)

# ----------------------------------------------------------------------------------
# plot results - brief
# ----------------------------------------------------------------------------------

x_var = 'PR'
x_label = 'Pressure ratio [-]'
x_convert = 1.0

y_vars = ["T_air_out", "w_exp", "w_pmp", "w_total"]
y_labels = ["Outlet Temp\n[K]", "Expansion work\n[kJ/kg-air]", "Pump work\n[kJ/kg-air]", "Total work\n[kJ/kg-air]"]
y_converts = [1.0, 1.0e-3, 1.0e-3, 1.0e-3]

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 7.48  # inches

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
        x = list(df2.loc[:, x_var] * x_convert)
        y = list(df2.loc[:, y_var] * y_convert)
        ax.plot(x, y, markeredgecolor=color, markerfacecolor=color)

    # Labels
    if i == 3:
        ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

# title
title = 'Near-isothermal Expander Performance\nInlet: ' + str(T_air_in) + ' K\nOutlet:' + str(p_air_out * 1e-3) + ' kPa'
f.suptitle(title)

# legend
patches = []
for j, ML in enumerate(MLs):
    patches.append(mpatches.Patch(color=colors[j], label=str(ML)))
leg = ax.legend(handles=patches, bbox_to_anchor=(0.5, -0.4), loc="upper center", title="Mass Loading Ratio", ncol=7)
plt.tight_layout()
plt.subplots_adjust(wspace=0.2, top=0.9)
plt.savefig('isothermal_exp_brief.png', DPI=600, bbox_extra_artists=leg)

# ----------------------------------------------------------------------------------
# plot results - full
# ----------------------------------------------------------------------------------

x_var = 'PR'
x_label = 'Pressure ratio [-]'
x_convert = 1.0

y_vars = ["p_air_in", "p_air_out", "T_air_in", "T_air_out", "n", "w_exp", "w_pmp", "w_total"]
y_labels = ["Inlet Pressure\n[kPa]", "Outlet Pressure\n[kPa]", "Inlet Temp\n[K]", "Outlet Temp\n[K]",
            "Polytropic exponent\n[-]", "Expansion work\n[kJ/kg-air]", "Pump work\n[kJ/kg-air]",
            "Total work\n[kJ/kg-air]"]
y_converts = [1.0e-3, 1.0e-3, 1.0, 1.0, 1.0, 1.0e-3, 1.0e-3, 1.0e-3]

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 7.48  # inches

# Create plot
f, a = plt.subplots(4, 2, sharex='col')
b = a.ravel()

# Set size
f.set_size_inches(width, height)

colors = sns.color_palette('colorblind')

for i, (y_var, y_label, y_convert) in enumerate(zip(y_vars, y_labels, y_converts)):
    ax = b[i]

    for j, ML in enumerate(MLs):
        color = colors[j]
        df2 = df[(df.loc[:, 'ML'] == ML)]
        x = list(df2.loc[:, x_var] * x_convert)
        y = list(df2.loc[:, y_var] * y_convert)
        ax.plot(x, y, markeredgecolor=color, markerfacecolor=color)

    # Labels
    if i == 6 or i == 7:
        ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

# Title
f.suptitle('Near-isothermal Expander Performance')

# legend
patches = []
for j, ML in enumerate(MLs):
    patches.append(mpatches.Patch(color=colors[j], label=str(ML)))
leg = ax.legend(handles=patches, bbox_to_anchor=(-0.25, -0.4), loc="upper center", title="Mass Loading Ratio", ncol=7)
plt.tight_layout()
plt.subplots_adjust(wspace=0.4, hspace=0.2, top=0.9)
plt.savefig('isothermal_exp_full.png', DPI=600, bbox_extra_artists=leg)
