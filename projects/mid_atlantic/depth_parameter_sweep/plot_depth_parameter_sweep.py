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
results_filename = "sweep_results.csv"

# figure output
DPI = 300  # Set resolution for saving figures

series_var = 'k'
series_dict = {0.01: '0.01 mD', 0.1: '0.1 mD', 1: '1 mD',
               10: '10 mD', 100: '100 mD', 1000: '1000 mD'}

# Set Color Palette
colors = sns.color_palette("colorblind")
colors = [colors[0], colors[1], colors[2], colors[3], colors[5], colors[4]]
# re-order palette to match series_dict.keys()
# colors = [colors[3], colors[1], (0, 0, 0), colors[9], colors[0]]

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
height = 7.5  # inches

x_vars = ["depth"]
x_labels = ["Depth (m)", ]
x_converts = [1.0]
x_limits = [[]]

y_vars = ["RTE", "m_dot", "r_f", "dp_well_avg", "dp_pipe_f_avg"]
y_labels = ["Round Trip\nEfficiency\n(%)", "Mass flow\n(kg/s)", "Bubble\nRadius\n(m)", "Aquifer\nPressure Drop\n(MPa)",
            "Pipe\n Pressure Loss\n(MPa)", ]
y_converts = [100.0, 1.0, 1.0, 1.0, 1.0]
y_limits = [[], [], [], [], []]

for ix in range(2):

    if ix == 0:
        savename = "Fig_Depth_Parameter_sweep_100MW.png"
        df_ix = df[df.loc[:, 'capacity_MW'] == 100]
    elif ix == 1:
        savename = "Fig_Depth_Parameter_sweep_200MW.png"
        df_ix = df[df.loc[:, 'capacity_MW'] == 200]
    #
    #
    # elif ix == 2:
    #     savename = "Fig_Perf_Results_expected2.png"
    #     df_ix = df[df.loc[:, 'k_type'] == 'expected']
    #     y_vars = [y_vars[2]]
    #     y_labels = [y_labels[2]]
    #     y_converts = [y_converts[2]]
    #     y_limits = [y_limits[2]]

    # Create plot
    f, a = plt.subplots(len(y_vars), len(x_vars), sharex='col', sharey='row', squeeze=False)

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
    markers = ['o', 's', 'd', '^', 'v', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'o', 'X']
    marker_size = 3.0
    markeredgewidth = 2.0

    count = 0
    # iterate through x-variables
    for i, (x_var, x_label, x_convert, x_limit) in enumerate(zip(x_vars, x_labels, x_converts, x_limits)):

        # iterate through y-variables
        for j, (y_var, y_label, y_convert, y_limit) in enumerate(zip(y_vars, y_labels, y_converts, y_limits)):

            # access subplot
            ax = a[j, i]

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
    # patches = []
    # for serie_label, serie_color in zip(entries, entry_colors):
    # for k, entry in enumerate(series_dict.values()):
    #     patches.append(mpatches.Patch(facecolor=colors[k], label=entry))
    symbols = []
    for k, entry in enumerate(series_dict.values()):
        symbols.append(mlines.Line2D([], [], color=colors[k], linestyle='', marker=markers[k], markersize=marker_size,
                                     markerfacecolor=colors[k], markeredgewidth=markeredgewidth,
                                     label=entry))

    # y_pos = j / 2 + 0.5
    # leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
    x_pos = -0.1
    leg = a[j, i].legend(handles=symbols, bbox_to_anchor=(x_pos, -0.5), ncol=6, loc='upper left',
                         title='Permeability')

    # Adjust layout
    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
    f.align_ylabels(a[:, 0])  # align y labels

    # Save Figure
    plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
    # plt.close()
