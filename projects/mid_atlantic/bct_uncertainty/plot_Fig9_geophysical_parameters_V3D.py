import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# =====================================
# user inputs
# =====================================
# data input
results_filename = "uncertainty_results_all.csv"
savename = "Fig9_geophysical_parameters_V3D.png"

# figure resolution
DPI = 400  # Set resolution for saving figures

x_var = "permeability_mD"
x_label = "Permeability (mD)"
x_convert = 1.0
x_limit = []
x_scale = 'log'

y_vars = ["porosity", "thickness_m",]
y_labels = ["Porosity (-)", "Thickness (m)"]
y_converts = [1.0, 1.0]
y_limits = [[], []]
y_scales = ['linear', 'log']

series_var = 'RTE'
series_convert = 100.0
series_label = "Efficiency (%)"

formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}

markersize = 2
# =====================================
# process data
# =====================================

# Import results
df = pd.read_csv(results_filename)

# Fill empty values as zero
df = df.fillna(0.0)

# Set efficiency to 0 for all errors
# df.loc[df.errors == False, 'RTE'] = 0.0

# Not interested in cases with thickness less than 5 m
# df = df.loc[df.thickness_m > 5.0]

# =====================================
# create plots
# =====================================

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 10.0  # inches
height = 6.5  # inches

# Create plot
f, a = plt.subplots(len(y_vars), len(df.sheet_name.unique()), sharex=True, sharey='row', squeeze=False)

# Set size
f.set_size_inches(width, height)

# Set style and context
sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

# Set Color Palette
colors = sns.color_palette("colorblind")

count = 0
# iterate through y-variables
for j, (y_var, y_label, y_convert, y_limit, y_scale) in enumerate(
        zip(y_vars, y_labels, y_converts, y_limits, y_scales)):

    # iterate through x-variables
    for i, (formation) in enumerate(df.sheet_name.unique()):

        # access subplot
        ax = a[j, i]

        # get data and convert
        # x = x_convert * df.loc[:, x_var]
        # y = y_convert * df.loc[:, y_var]

        # plot successful combinations
        df2 = df[(df.loc[:, 'RTE'] > 0.0) & (df.loc[:, 'sheet_name'] == formation)]
        x = x_convert * df2.loc[:, x_var]
        y = y_convert * df2.loc[:, y_var]
        ax.scatter(x, y, c='black', s=markersize, marker='.')

        # plot failures
        df2 = df[(df.loc[:, 'RTE'] <= 0.0) & (df.loc[:, 'sheet_name'] == formation)]
        x = x_convert * df2.loc[:, x_var]
        y = y_convert * df2.loc[:, y_var]
        ax.scatter(x, y, c='red', s=markersize, marker='.')

        # axes scales
        ax.set_xscale(x_scale)
        ax.set_yscale(y_scale)

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
        if len(y_limit) == 2:
            ax.set_ylim(bottom=y_limit[0], top=y_limit[1])

        # top labels
        if j == 0:
            plt.text(0.5, 1.1, formation_dict[formation], horizontalalignment='center', verticalalignment='center',
                     transform=ax.transAxes, fontsize='medium', fontweight='bold')

        # Caption labels
        caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        plt.text(0.1, 0.9, caption_labels[count], horizontalalignment='center', verticalalignment='center',
                 transform=ax.transAxes, fontsize='medium', fontweight='bold')
        count = count + 1

# Legend
patches = [mpatches.Patch(color='black', label='Feasible'), mpatches.Patch(color='red', label='Infeasible')]
a[1, 1].legend(handles=patches, bbox_to_anchor=(0.5, -0.275), loc="upper center", ncol=2)

# Adjust layout
# plt.tight_layout()
plt.subplots_adjust(top=0.9,
bottom=0.15,
left=0.125,
right=0.9,
hspace=0.2,
wspace=0.2)
f.align_ylabels(a[:, 0])  # align y labels

# Save Figure
# plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
plt.savefig(savename, dpi=DPI)
# plt.close()