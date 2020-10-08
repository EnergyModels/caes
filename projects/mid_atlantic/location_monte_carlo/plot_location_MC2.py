# General imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
results_filename = "mc_results.csv"
savename = "Fig7_location_MC.png"
# =============================================================================#
y_vars = ["RTE", "duration", "kW_out_avg"]
y_labels = ["Efficiency\n(%)", "Duration\n(hr)", "Power\n(MW)"]
y_converts = [100.0, 1.0, 1e-3]
y_limits = [[], [], []]

df = pd.read_csv(results_filename)
df.loc[:, 'duration'] = df.loc[:, 'kWh_out'] / df.loc[:, 'kW_out_avg']
df.loc[:, 'Analysis Case'] = df.loc[:, 'sheetname']



f, a = plt.subplots(1, 3, sharey=True)
a = a.ravel()

# Set size
f.set_size_inches(width, height)
legend = [False, True, False]
for ax, y_var, y_label, y_convert, y_limit, leg in zip(a, y_vars, y_labels, y_converts, y_limits, legend):
    df.loc[:, y_var] = df.loc[:, y_var] * y_convert
    sns.histplot(data=df, x=y_var, ax=ax, hue='Analysis Case', multiple='dodge', element='step', fill=False, legend=leg)
    ax.set_xlabel(y_label)
    # sns.distplot(df[y_var], ax=ax)

a[1].legend(bbox_to_anchor=(0.5, -0.3), ncol=3)

# Save Figure
plt.savefig(savename, dpi=DPI)
# plt.close()

df = df.fillna(0.0)
for case in df.loc[:, 'Analysis Case'].unique():
    ind = (df.loc[:, 'Analysis Case'] == case) & (df.loc[:, 'RTE'] == 0.0)
    print(case)
    print(str(sum(ind)))
