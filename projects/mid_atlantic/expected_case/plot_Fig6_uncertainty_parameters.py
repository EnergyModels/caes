import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# =====================================
# user inputs
# =====================================
# data input
results_filename = "uncertainty_results_all.csv"
savename = "Fig6_uncertainty_parameters.png"

# figure resolution
DPI = 400  # Set resolution for saving figures

x_vars = ["T_grad_m", "p_hydro_grad", "p_frac_grad", "loss_m_air", "depth_m", "thickness_m", "porosity",
          "permeability_mD"]
x_labels = ["Geothermal Gradient\n(deg C/km)", "Pressure Gradient\n(MPa/km)", "Frac Gradient\n(MPa/km)",
            "Air leakage\n(%)", "Depth\n(m)", "Thickness\n(m)", "Porosity\n(-)", "Permeability\n(mD)"]
x_converts = [1000.0, 1.0, 1.0, 100.0, 1.0, 1.0, 1.0, 1.0]
x_limits = [[], [], [], [], [0.0, 5500.0], [], [], [], ]
x_scales = ["linear", "linear", "linear", "linear", "linear", "log", "linear", "log"]

y_var = "RTE"
y_label = "RTE [%]"
y_convert = 100.0
y_limit = [40.0, 80.0]
y_scale = 'linear'

formations = ['MK1-3', 'LK1',  'UJ1']
formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}
colors = sns.color_palette('colorblind')
markersize = 1

# =====================================
# process data
# =====================================

# Import results
df = pd.read_csv(results_filename)

# Fill empty values as zero
df = df.fillna(0.0)

# Remove efficiency values == 0
df = df[df.loc[:, 'RTE'] > 0.0]

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
f, a = plt.subplots(2, 4, sharey=True, squeeze=False)
a = a.ravel()

# Set size
f.set_size_inches(width, height)

# Set style and context
sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

count = 0
# iterate through x-variables
for i, (x_var, x_label, x_convert, x_limit, x_scale) in enumerate(
        zip(x_vars, x_labels, x_converts, x_limits, x_scales)):

    # access subplot
    ax = a[i]

    for k, (formation, color) in enumerate(zip(formations, colors)):
        df2 = df[df.loc[:, 'sheet_name'] == formation]

        # get data and convert
        x = x_convert * df2.loc[:, x_var]
        y = y_convert * df2.loc[:, y_var]
        im = ax.scatter(x, y, c=[color], s=markersize, marker='.')

    # axes scales
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)

    # axes labels
    # x-axis labels
    ax.set_xlabel(x_label)

    # y-axis labels (only left side)
    if i == 0 or i == 4:
        ax.set_ylabel(y_label)

    # Despine and remove ticks
    sns.despine(ax=ax, )
    ax.tick_params(top=False, right=False)

    # Axes limits
    if len(y_limit) == 2:
        ax.set_ylim(bottom=y_limit[0], top=y_limit[1])

    if len(x_limit) == 2:
        ax.set_xlim(left=x_limit[0], right=x_limit[1])

    # Caption labels
    caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
    plt.text(0.1, 0.98, caption_labels[count], horizontalalignment='center', verticalalignment='center',
             transform=ax.transAxes, fontsize='medium', fontweight='bold')
    count = count + 1

    # # Add vertical line for depth
    # if i == 4 and len(y_limit) == 2:
    #     x = [1500, 1500]
    #     ax.plot(x, y_limit, 'k', linestyle='--')
    #     dx = 0
    #     dy = 4
    #     ax.text(x[0] - dx, y_limit[1] - dy, '3 stg ', horizontalalignment='right')
    #     ax.text(x[0] + dx, y_limit[1] - dy, ' 4 stg', horizontalalignment='left')

# Legend
# y_pos = j / 2 + 0.5
# leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
# x_pos = -0.1
# leg = a[j, i].legend(bbox_to_anchor=(x_pos, -0.6), ncol=3, loc='upper center')

# Legend
patches = [mpatches.Patch(color=colors[0], label=formation_dict[formations[0]]),
           mpatches.Patch(color=colors[1], label=formation_dict[formations[1]]),
           mpatches.Patch(color=colors[2], label=formation_dict[formations[2]])]
a[5].legend(handles=patches, bbox_to_anchor=(1.0, -0.3), loc="upper center", ncol=3)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9, bottom=0.15, left=0.126, right=0.89, hspace=0.3, wspace=0.214)
# f.align_ylabels(a[:, 0])  # align y labels

# Save Figure
# plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
plt.savefig(savename, dpi=DPI)
# plt.close()
