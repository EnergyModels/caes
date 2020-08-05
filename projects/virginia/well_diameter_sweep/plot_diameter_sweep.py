import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches

# =====================================
# user inputs
# =====================================
# data input
results_filename = "sweep_results.csv"

# figure output
savename = "Fig_Perf_Results.png"
DPI = 600  # Set resolution for saving figures

x_vars = ["m_dot", "r_f", "r_w"]
x_labels = ["Mass flow\n(kg/s)", "Formation radius\n(m)", "Wellbore radius\n(m)"]
x_converts = [1.0, 1.0, 1.0]
x_limits = [[], [], []]

y_vars = ["RTE", "kW_in_avg", "kWh_in"]
y_labels = ["Efficiency\n(%)", "Power Rating\n(MW)", "Energy Storage\n(MWh)"]
y_converts = [100.0, 1.0e-3, 1.0e-3]
y_limits = [[], [], []]

series_var = 'sheetname'
series_dict = {'low_k': '0.5 (minimium)', 'iowa_k': '3 (Iowa)', 'med_low_k': '38.3 (expected)',
               'med_high_k': '339 (average)', 'high_k': '2514 (maximum)'}

# =====================================
# process data
# =====================================

# Import results
df = pd.read_csv(results_filename)

# Filter Results with errors
df = df[df.errors == False]

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
height = 5.5  # inches

# Create plot
f, a = plt.subplots(len(y_vars), len(x_vars), sharex='col', sharey='row')

# Set size
f.set_size_inches(width, height)

# Set style and context
sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

# Set Color Palette
colors = sns.color_palette()
# re-order palette
colors = [colors[3], colors[1], (0, 0, 0), colors[9], colors[0]]
# colors = sns.diverging_palette(250, 15, n=5, center="dark")
# colors = [[215, 25, 28], [253, 174, 97], [255, 255, 191], [171, 217, 233], [44, 123, 182]]
# colors_hex = ['#d7191c','#fdae61','#252525','#abd9e9','#2c7bb6']
# colors = sns.color_palette(colors_hex).as_hex()

# Set marker shapes and sizes
markers = ['.', '.', '.', '.', '.']
# markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'o', 'X']
marker_size = 2
markeredgewidth = 0.5

count = 0
# iterate through x-variables
for i, (x_var, x_label, x_convert, x_limit) in enumerate(zip(x_vars, x_labels, x_converts, x_limits)):

    # iterate through y-variables
    for j, (y_var, y_label, y_convert, y_limit) in enumerate(zip(y_vars, y_labels, y_converts, y_limits)):

        # access subplot
        ax = a[j, i]

        # iterate through series
        for k, (serie, color, marker) in enumerate(zip(series, colors, markers)):
            ind = df.loc[:, series_var] == serie
            x = x_convert * df.loc[ind, x_var]
            y = y_convert * df.loc[ind, y_var]
            ax.plot(x, y, linestyle='', marker=marker, markersize=marker_size,
                    markeredgewidth=markeredgewidth, markeredgecolor=color, markerfacecolor='None',
                    label=series_dict[serie])

        # axes labels
        # x-axis labels (only bottom)
        if j == len(y_vars) - 1:
            ax.set_xlabel(x_label)
        else:
            ax.get_xaxis().set_visible(False)

        # y-axis labels (only left side)
        if i == 0:
            ax.set_ylabel(y_label)
        else:
            ax.get_yaxis().set_visible(False)

        # Despine and remove ticks
        sns.despine(ax=ax, )
        ax.tick_params(top=False, right=False)

        # Axes limits

        # Caption labels
        caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        plt.text(-0.1, 1.00, caption_labels[count], horizontalalignment='center', verticalalignment='center',
                 transform=ax.transAxes, fontsize='medium', fontweight='bold')
        count = count + 1

# Legend
patches = []
# for serie_label, serie_color in zip(entries, entry_colors):
for k, entry in enumerate(series_dict.values()):
    patches.append(mpatches.Patch(facecolor=colors[k], label=entry))
# y_pos = j / 2 + 0.5
# leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
x_pos = -0.1
leg = a[j, i].legend(handles=patches, bbox_to_anchor=(x_pos, -0.5), ncol=5, loc='upper center',
                     title='Permeability (mD)')

# Adjust layout
plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
f.align_ylabels(a[:, 0])  # align y labels

# Save Figure
plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
# plt.close()
