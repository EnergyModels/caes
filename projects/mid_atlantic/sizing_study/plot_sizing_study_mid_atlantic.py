import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches

# =====================================
# user inputs
# =====================================
# data input
results_filename = "sizing_study_results.csv"

# figure output
DPI = 300  # Set resolution for saving figures

series_var = 'duration_hr'
series_dict = {10: '10 hr (0.4 days)', 24: '24 hr (1 day)', 48: '48 hr (2 days)',
               72: '72 hr (3 days)', 168: '168 hr (1 week)'}

# Set Color Palette
colors = sns.color_palette("colorblind")
colors = [colors[0],colors[1],colors[2],colors[3],colors[5]]
# re-order palette to match series_dict.keys()
# colors = [colors[3], colors[1], (0, 0, 0), colors[9], colors[0]]

# =====================================
# process data
# =====================================

# Import results
df = pd.read_csv(results_filename)

# Filter Results with errors
df = df[df.errors == False]

# Filter Results with efficiencies less than 10% - not worth considering
# df = df[df.RTE >= 0.1]

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

x_vars = ["kW_in_avg"]
x_labels = ["Power Rating\n(MW)", ]
x_converts = [1e-3]
x_limits = [[]]

y_vars = ["m_dot", "r_f", "RTE"]
y_labels = ["Mass flow\n(kg/s)", "Formation radius\n(m)", "Efficiency\n(%)", ]
y_converts = [1.0, 1.0, 100.0]
y_limits = [[], [], []]

for ix in range(3):

    if ix == 0:
        savename = "Fig_Perf_Results_expected.png"
        df_ix = df[df.loc[:, 'k_type'] == 'expected']
    elif ix == 1:
        savename = "Fig_Perf_Results_all.png"
        # df_ix = df[df.loc[:, 'k_type'] == 'expected']
        df_ix = df

    elif ix == 2:
        savename = "Fig_Perf_Results_expected2.png"
        df_ix = df[df.loc[:, 'k_type'] == 'expected']
        y_vars = [y_vars[2]]
        y_labels = [y_labels[2]]
        y_converts = [y_converts[2]]
        y_limits = [y_limits[2]]

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
    markers = ['.', '.', '.', '.', '.']
    # markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'o', 'X']
    marker_size = 7.5
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
    leg = a[j, i].legend(handles=patches, bbox_to_anchor=(x_pos, -0.5), ncol=5, loc='upper left',
                         title='Duration)')

    # Adjust layout
    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
    f.align_ylabels(a[:, 0])  # align y labels

    # Save Figure
    plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
    # plt.close()
