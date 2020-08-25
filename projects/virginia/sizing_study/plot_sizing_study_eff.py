import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# =====================================
# user inputs
# =====================================
# data input
results_filename = "sizing_study_results.csv"
savename = "Fig_Sizing_study_efficiency.png"

# figure output
DPI = 400  # Set resolution for saving figures

series_var = 'duration_hr'
# series_dict = {10: '10 hr (0.4 days)', 24: '24 hr (1 day)', 48: '48 hr (2 days)',
#                72: '72 hr (3 days)', 168: '168 hr (1 week)'}

series_dict = {10: '10 hr (0.4 days)', 24: '24 hr (1 day)', 168: '168 hr (1 week)'}

# Set Color Palette
colors = sns.color_palette("colorblind")
colors = [colors[2], colors[1], colors[3], colors[3], colors[5]]
# re-order palette to match series_dict.keys()
# colors = [colors[3], colors[1], (0, 0, 0), colors[9], colors[0]]

# =====================================
# process data
# =====================================

# Import results
df = pd.read_csv(results_filename)

# Filter Results with errors
df = df[df.errors == False]

# Only plot expected value of permeability
df_ix = df[df.loc[:, 'k_type'] == 'expected']

# get list of unique series
series = series_dict.keys()

# =====================================
# create plots
# =====================================

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 4.0  # inches

x_var = "kW_out_avg"
x_label = "Power Rating (MW)"
x_convert = 1e-3
x_limit = []

y_var = "RTE"
y_label = "Efficiency (%)"
y_convert = 100.0
y_limit = []

# Create plot
f, a = plt.subplots(1, 1, sharex='col', sharey='row', squeeze=False)
ax = a[0][0]

# Set size
f.set_size_inches(width, height)

# Set style and context
sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

# colors = sns.diverging_palette(250, 15, n=5, center="dark")
# colors = [[215, 25, 28], [253, 174, 97], [255, 255, 191], [171, 217, 233], [44, 123, 182]]
# colors_hex = ['#d7191c','#fdae61','#252525','#abd9e9','#2c7bb6']
# colors = sns.color_palette(colors_hex).as_hex()

# Set marker shapes and sizes
# markers = ['.', '.', '.', '.', '.']
markers = ['^', '.', 'v', '^', 'v', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'o', 'X']
marker_size = 3.0
markeredgewidth = 2.0

# iterate through series
for k, (serie, color, marker) in enumerate(zip(series, colors, markers)):
    ind = df_ix.loc[:, series_var] == serie
    x = x_convert * df_ix.loc[ind, x_var]
    y = y_convert * df_ix.loc[ind, y_var]
    ax.plot(x, y, linestyle='-', color=color, marker=marker, markersize=marker_size,
            markeredgewidth=markeredgewidth, markeredgecolor=color, markerfacecolor='None',
            label=series_dict[serie])

# axes labels
# x-axis labels (only bottom)
ax.set_xlabel(x_label)

# y-axis labels (only left side)
ax.set_ylabel(y_label)

# Despine and remove ticks
sns.despine(ax=ax, )
ax.tick_params(top=False, right=False)

# Legend
# patches = []
# for serie_label, serie_color in zip(entries, entry_colors):
# for k, entry in enumerate(series_dict.values()):
#     patches.append(mpatches.Patch(facecolor=colors[k], label=entry))
symbols = []
for k, entry in enumerate(series_dict.values()):
    symbols.append(mlines.Line2D([], [], color=colors[k], linestyle='-', marker=markers[k], markersize=marker_size,
                                 markerfacecolor=colors[k], markeredgewidth=markeredgewidth,
                                 label=entry))

# y_pos = j / 2 + 0.5
# leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
x_pos = -0.1
leg = ax.legend(handles=symbols, bbox_to_anchor=(0.05, 0.05), ncol=1, loc='lower left',
                title='Storage Duration)')

# Adjust layout
# plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
# f.align_ylabels(a[:, 0])  # align y labels

# Save Figure
plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
# plt.close()
