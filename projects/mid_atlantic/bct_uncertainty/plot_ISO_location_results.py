# General imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.lines as mlines

# Set Color Palette
colors = sns.color_palette("colorblind")
# Set resolution for saving figures
DPI = 300

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 5.5  # inches

# %%=============================================================================#
# Figure 6 - LCOE
results_filename = "uncertainty_results_all.csv"
savename = "Fig8_ISO_location_results.png"
# =============================================================================#
y_vars = ["RTE", "duration", "kW_out_avg"]
y_labels = ["Efficiency\n(%)", "Duration\n(hr)", "Power\n(MW)"]
y_converts = [100.0, 1.0, 1e-3]
y_limits = [[], [], []]

pal = 'colorblind'

df_raw = pd.read_csv(results_filename)

# select locations of interest and provide case to label
cases = ['PJM', ' New England ISO', 'ISO NY']
sheet_names = ['LK1', 'LK1', 'LK1']
xs = [-49904.42, 385475.58, 147995.58]
ys = [4108774.11, 4504574.11, 4464994.11]

df = pd.DataFrame()
for case, sheet_name, x, y in zip(cases, sheet_names, xs, ys):
    df_slice = df_raw[(df_raw.loc[:, 'sheet_name'] == sheet_name) &
                      (df_raw.loc[:, 'X (m)'] == x) &
                      (df_raw.loc[:, 'Y (m)'] == y)]
    if len(df_slice) > 0:
        df_slice.loc[:, 'Analysis Case'] = case
        df = df.append(df_slice)

# calculate additional
df.loc[:, 'duration'] = df.loc[:, 'kWh_out'] / df.loc[:, 'kW_out_avg']
# filla in nan
df.fillna(0.0)

# save location results
df.to_csv('ISO_location_results.csv')

f, a = plt.subplots(1, 3, sharey=True)
a = a.ravel()

# Set size
f.set_size_inches(width, height)
legend = [False, False, False]
for ax, y_var, y_label, y_convert, y_limit, leg in zip(a, y_vars, y_labels, y_converts, y_limits, legend):
    df.loc[:, y_var] = df.loc[:, y_var] * y_convert
    sns.histplot(data=df, x=y_var, ax=ax, hue='Analysis Case', multiple='dodge', element='step', fill=False, legend=leg,
                 palette=pal,)
    ax.set_xlabel(y_label)
    # sns.distplot(df[y_var], ax=ax)

# a[1].legend(bbox_to_anchor=(0.5, -0.15), ncol=3)

lines = []
for case, color in zip(cases, sns.color_palette(pal)):
    lines.append(mlines.Line2D([], [], color=color, linestyle='-', marker='None', markersize=9,
                               markerfacecolor='None', markeredgewidth=1.5,
                               label=case))
a[1].legend(handles=lines, bbox_to_anchor=(0.5, -0.15), loc="upper center", title='Location', ncol=3)

plt.subplots_adjust(top=0.88, bottom=0.23, left=0.1, right=0.9, hspace=0.205, wspace=0.2)

# Save Figure
plt.savefig(savename, dpi=DPI)
# plt.close()

df = df.fillna(0.0)
for case in df.loc[:, 'Analysis Case'].unique():
    ind = (df.loc[:, 'Analysis Case'] == case) & (df.loc[:, 'RTE'] == 0.0)
    print(case)
    print(str(sum(ind)))
