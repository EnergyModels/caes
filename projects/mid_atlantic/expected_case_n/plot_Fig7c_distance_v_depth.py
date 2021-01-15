import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset
from math import pi
import numpy as np
import matplotlib.colors as colors
import matplotlib.patches as mpatches

df = pd.read_csv('all_analysis.csv')

# f, a = plt.subplots(2,1)
# a = a.ravel()
#
# sns.scatterplot(data=df, x='NEAR_DIST',y='feasible_fr', hue='NEAR_FC', ax=a[0])
#
# sns.scatterplot(data=df, x='NEAR_DIST',y='RASTERVALU', hue='NEAR_FC', ax=a[1])

# conversions and column renaming
df.loc[:, 'Distance to shore (km)'] = df.loc[:, 'NEAR_DIST'] / 1000.0
df.loc[:, 'Water depth (m)'] = df.loc[:, 'RASTERVALU']
df.loc[:, 'Feasibility (%)'] = df.loc[:, 'feasible_fr'] * 100.0
df.loc[:, 'Formation (-)'] = df.loc[:, 'formation']
df.loc[:, 'Nearest State (-)'] = df.loc[:, 'NEAR_FC']

loc_dict = {'VA_shore': 'Virginia', 'MD_shore': 'Maryland', 'NJ_shore': 'New Jersey', 'DE_shore': 'Delaware',
            'NY_shore': 'New York', 'MA_shore': 'Massachusetts', 'RI_shore': 'Rhode Island'}

formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}

# rename
for loc in df.loc[:, 'Nearest State (-)'].unique():
    ind = df.loc[:, 'Nearest State (-)'] == loc
    df.loc[ind, 'Nearest State (-)'] = loc_dict[loc]

# rename
for formation in df.loc[:, 'Formation (-)'].unique():
    ind = df.loc[:, 'Formation (-)'] == formation
    df.loc[ind, 'Formation (-)'] = formation_dict[formation]

# Filter data with feasibility greater than 0.8
# df = df[df.loc[:,'Feasibility (%)']>=0.8]

# Filter data with mean RTE greater than 0.5
# df = df[df.loc[:, 'RTE_mean'] >= 0.5]

sns.histplot(df, x='Water depth (m)')

df.loc[:, 'RTE [%]'] = df.loc[:, 'RTE_mean']

df.loc[:, 'Water depth'] = '> 60m'
df.loc[df.loc[:, 'Water depth (m)'] > -60.0, 'Water depth'] = '30m - 60m'
df.loc[df.loc[:, 'Water depth (m)'] > -30.0, 'Water depth'] = '<30 m'

# sns.histplot(df, x='RTE [%]', hue='Water depth', hue_order=['<30 m', '30m - 60m', '> 60m'])

palette_rgb = np.array([[69, 117, 180],
                        [145, 191, 219],
                        [224, 243, 248]])
palette_hex = []
for rgb in palette_rgb:
    palette_hex.append(colors.rgb2hex(rgb / 255))
# cmap = colors.ListedColormap(palette_hex)
# Calculate storage potential
frac = 0.1  # fraction of grid available for storage
A_grid = 20000 * 20000  # each square is 20 km by 20 km
well_MWh = 200 * 24  # 200 MW at 24 hour duration

df.loc[:, 'A_well'] = pi * df.loc[:, 'r_f'] ** 2
df.loc[:, 'n_wells'] = frac * A_grid / df.loc[:, 'A_well']
df.loc[:, 'MWh'] = df.loc[:, 'n_wells'] * well_MWh

# entries = ['RTE', 'MWh', 'Depth']
# RTE_bins = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
# RTE_labels = ['40-45', '45-50', '50-55', '55-60', '60-65']
# Depth_bins = [0.0, -30.0, -60.0, -90.0, -120.0]
# # Depth_labels = ['0-30m', '30-60m', '60-90m', '90-120m']
# df_smry = pd.DataFrame(columns=entries)
# for i in range(len(RTE_bins) - 1):
#     for j in range(len(Depth_bins) - 1):
#         # Select relevant indices
#         ind = (RTE_bins[i] <= df.loc[:, 'RTE_mean']) & (df.loc[:, 'RTE_mean'] < RTE_bins[i + 1]) \
#               & (Depth_bins[j + 1] < df.loc[:, 'Water depth (m)']) & (df.loc[:, 'Water depth (m)'] <= Depth_bins[j])
#
#         # store result
#         s = pd.Series(index=entries)
#         s['RTE'] = RTE_labels[i]
#         s['Depth'] = Depth_bins[j]
#         s['MWh'] = df.loc[ind, 'MWh'].sum()
#         df_smry = df_smry.append(s, ignore_index=True)

# sns.barplot(data=df_smry, x='Depth', y='MWh', hue='RTE')
#
# for i, RTE_label in enumerate(RTE_labels):
#     ind = df_smry.loc[:, 'RTE'] == RTE_label
#     x = df_smry.loc[ind, 'Depth'] * -1.0
#     y = df_smry.loc[ind, 'MWh']
#     if i == 0:
#         plt.bar(x, y, width=1.0, label=RTE_label)
#     else:
#         plt.bar(x, y, bottom=y_prev, width=1.0, label=RTE_label)
#
#     y_prev = y

entries = ['RTE', 'MWh', 'Depth']
RTE_bins = [0.40, 0.50, 0.60, 0.65]
RTE_labels = ['40 - 50%', '50 - 60%', '60 - 70%']
# Depth_bins = [0.0, -30.0, -60.0, -90.0, -120.0]
Depth_bins = np.arange(0.0, -600.1, -10.0)
df_smry = pd.DataFrame(index=RTE_labels, columns=Depth_bins[:-1])
for i in range(len(RTE_bins) - 1):
    for j in range(len(Depth_bins) - 1):
        # Select relevant indices
        ind = (RTE_bins[i] <= df.loc[:, 'RTE_mean']) & (df.loc[:, 'RTE_mean'] < RTE_bins[i + 1]) \
              & (Depth_bins[j + 1] < df.loc[:, 'Water depth (m)']) & (df.loc[:, 'Water depth (m)'] <= Depth_bins[j])

        # store result
        df_smry.loc[RTE_labels[i], Depth_bins[j]] = df.loc[ind, 'MWh'].sum()

# sns.barplot(data=df_smry, x='Depth', y='MWh', hue='RTE')

widths = []
for j in range(len(Depth_bins) - 1):
    widths.append(Depth_bins[j] - Depth_bins[j + 1])

for i, index in enumerate(reversed(df_smry.index)):
    # ind = df_smry.loc[:, 'RTE'] == RTE_label
    x = df_smry.columns * -1.0
    height = df_smry.loc[index, :] / 1e6
    if i == 0:
        plt.bar(x, height, width=widths, label=index, align='edge', color=palette_hex[i])
        bottom = height
    else:
        plt.bar(x, height, bottom=bottom, width=widths, label=index, align='edge', color=palette_hex[i])
        bottom = bottom + height

    # Add outline
    plt.step(x, bottom, 'k', where='post')

# labels
plt.xlabel('Water depth (m)')
plt.ylabel('Storage capacity (TWh)')

# limits
xlims = [0.0, Depth_bins[-1] * -1.0]
ylims = [0.0, 350]
plt.xlim(left=xlims[0], right=xlims[1])
plt.ylim(bottom=ylims[0], top=ylims[1])

# Additional line
plt.plot([30.0, 30.0], ylims, 'k--')

# set background color
ax = plt.gca()
ax.set_facecolor((0.8, 0.8, 0.8))

# create legend
patches = [mpatches.Patch(edgecolor='black', facecolor=palette_hex[2], label=RTE_labels[0]),
           mpatches.Patch(edgecolor='black', facecolor=palette_hex[1], label=RTE_labels[1]),
           mpatches.Patch(edgecolor='black', facecolor=palette_hex[0], label=RTE_labels[2])]
leg1 = ax.legend(handles=patches, bbox_to_anchor=(1.0, 1.0), loc="upper right", title='Round Trip Efficiency')


savename = "Fig7c_Distance_v_depth.png"
plt.savefig(savename, dpi=400)
