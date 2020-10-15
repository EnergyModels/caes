import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================
# user inputs
# =====================================
# data input
results_filename = "uncertainty_results_all.csv"
savename = "Fig9_geophysical_parameters_V3B.png"

# figure resolution
DPI = 400  # Set resolution for saving figures

x_vars = ["depth_m", "thickness_m", "porosity", "permeability_mD", "T_grad_m", "p_hydro_grad", "p_frac_grad",
          "loss_m_air"]
x_labels = ["Depth\n(m)", "Thickness\n(m)", "Porosity\n(-)", "Permeability\n(mD)", "Thermal Gradient\n(deg C/km)",
            "Pressure Gradient\n(MPa/km)", "Frac Gradient\n(MPa/km)",
            "Air leakage\n(kg/s)"]
x_converts = [1.0, 1.0, 1.0, 1.0, 1000.0, 1.0, 1.0, 100.0, ]
x_limits = [[], [], [], [], [], [], [], []]
x_scales = ['linear', 'log', 'linear', 'log', 'linear', 'linear', 'linear', 'linear']

y_vars = ["depth_m", "thickness_m", "porosity", "permeability_mD", "T_grad_m", "p_hydro_grad", "p_frac_grad",
          "loss_m_air"]
y_labels = ["Depth\n(m)", "Thickness\n(m)", "Porosity\n(-)", "Permeability\n(mD)", "Thermal Gradient\n(deg C/km)",
            "Pressure Gradient\n(MPa/km)", "Frac Gradient\n(MPa/km)",
            "Air leakage\n(kg/s)"]
y_converts = [1.0, 1.0, 1.0, 1.0, 1000.0, 1.0, 1.0, 100.0, ]
y_limits = [[], [], [], [], [], [], [], []]
y_scales = ['linear', 'log', 'linear', 'log', 'linear', 'linear', 'linear', 'linear']

series_var = 'RTE'
series_convert = 100.0
series_label = "Efficiency (%)"

markersize = 1
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
df = df.loc[df.thickness_m > 5.0]

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
f, a = plt.subplots(len(y_vars), len(x_vars), sharex='col', sharey='row', constrained_layout=True)

# Set size
f.set_size_inches(width, height)

# Set style and context
sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

# Set Color Palette
colors = sns.color_palette("colorblind")

count = 0
# iterate through x-variables
for i, (x_var, x_label, x_convert, x_limit, x_scale) in enumerate(
        zip(x_vars, x_labels, x_converts, x_limits, x_scales)):

    # iterate through y-variables
    for j, (y_var, y_label, y_convert, y_limit, y_scale) in enumerate(
            zip(y_vars, y_labels, y_converts, y_limits, y_scales)):

        # access subplot
        ax = a[j, i]

        # get data and convert
        # x = x_convert * df.loc[:, x_var]
        # y = y_convert * df.loc[:, y_var]

        # plot successful combinations
        ind = df.loc[:, 'RTE'] > 0.0
        x = x_convert * df.loc[ind, x_var]
        y = y_convert * df.loc[ind, y_var]
        ax.scatter(x, y, c='black', s=markersize, marker='o')

        # plot failures
        ind = df.loc[:, 'RTE'] <= 0.0
        x = x_convert * df.loc[ind, x_var]
        y = y_convert * df.loc[ind, y_var]
        ax.scatter(x, y, c='red', s=markersize, marker='X')

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

        # Caption labels
        # caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        # plt.text(0.1, 0.9, caption_labels[count], horizontalalignment='center', verticalalignment='center',
        #          transform=ax.transAxes, fontsize='medium', fontweight='bold')
        count = count + 1

        # # Add vertical line for depth
        # if i == 0 and len(y_limit) == 2:
        #     x = [1500, 1500]
        #     ax.plot(x, y_limit, 'k', linestyle='--')
        # if i == 0 and j == 0:
        #     dx = 0
        #     dy = 2
        #     ax.text(x[0] - dx, y_limit[1] - dy, '3 stages   ', horizontalalignment='right')
        #     ax.text(x[0] + dx, y_limit[1] - dy, '   4 stages', horizontalalignment='left')

# Legend
# y_pos = j / 2 + 0.5
# leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
# x_pos = -0.1
# leg = a[j, i].legend(bbox_to_anchor=(x_pos, -0.6), ncol=3, loc='upper center')

# Colorbar
# collect all right hand side axes
# a_cbar = []
# for ax in a:
#     a_cbar.append(ax[-1])
# cbar = f.colorbar(im, ax=a_cbar, location='right', shrink=0.6)
# cbar.ax.set_ylabel(series_label)

# Adjust layout
# plt.tight_layout()
# plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
f.align_ylabels(a[:, 0])  # align y labels

# Save Figure
# plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
plt.savefig(savename, dpi=DPI)
# plt.close()
