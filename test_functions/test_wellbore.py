import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from caes import wellbore

# Wellbore test
T_air_in = 273.15 + 25.0  # [K]
f = 0.015  # [-]
D = 18.0 / 12.0 * 0.3048  # [m]

# Pressure ratios
depths = np.arange(100, 1500, 50)  # well depths
m_dots = np.arange(1.0, 10.0, 1.0)  # mass flow rates [kg/s]

# Store results
entries = ['depth', 'm_dot', 'T_air_in', 'p_air_in', 'delta_p']
df = pd.DataFrame(columns=entries)

for depth in depths:
    for m_dot in m_dots:
        # compute inlet pressure
        rho = 1000  # water density [kg/m3]
        g = 9.81  # gravitational constant [m/s^2]
        p_air_in = rho * g * depth

        # compute performance
        delta_p = wellbore(T_air_in, p_air_in, depth, D, m_dot, f=f)

        # store results
        s = pd.Series(index=entries, dtype='float64')
        s['depth'] = depth
        s['m_dot'] = m_dot
        s['T_air_in'] = T_air_in
        s['p_air_in'] = p_air_in
        s['delta_p'] = delta_p
        df = df.append(s, ignore_index=True)

# ----------------------------------------------------------------------------------
# plot results - brief
# ----------------------------------------------------------------------------------

x_var = 'depth'
x_label = 'Well depth [m]'
x_convert = 1.0

y_vars = ["T_air_in", "p_air_in", "delta_p"]
y_labels = ["Inlet Temp\n[K]", "Inlet pressure\n[kPa]", "Pressure drop\n[kPa]"]
y_converts = [1.0, 1.0e-3, 1.0e-3]

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 7.48  # inches

# Create plot
fig, a = plt.subplots(3, 1, sharex='col')

# Set size
fig.set_size_inches(width, height)

colors = sns.color_palette('colorblind')

for i, (y_var, y_label, y_convert) in enumerate(zip(y_vars, y_labels, y_converts)):
    ax = a[i]

    for j, m_dot in enumerate(m_dots):
        color = colors[j]
        df2 = df[(df.loc[:, 'm_dot'] == m_dot)]
        x = list(df2.loc[:, x_var] * x_convert)
        y = list(df2.loc[:, y_var] * y_convert)
        ax.plot(x, y, markeredgecolor=color, markerfacecolor=color)

    # Labels
    if i == 2:
        ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

# title
title = 'Wellbore Performance\nFriction coefficient: ' + str(f)
fig.suptitle(title)

# legend
patches = []
for j, m_dot in enumerate(m_dots):
    patches.append(mpatches.Patch(color=colors[j], label=str(m_dot)))
leg = ax.legend(handles=patches, bbox_to_anchor=(0.5, -0.4), loc="upper center", title="Mass flow rate [kg/s]", ncol=7)
plt.tight_layout()
plt.subplots_adjust(wspace=0.2, top=0.9)
plt.savefig('wellbore_injection.png', DPI=600, bbox_extra_artists=leg)
