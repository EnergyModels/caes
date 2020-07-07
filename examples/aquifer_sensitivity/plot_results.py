import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

DPI = 300
# %%=============================================================================#
# Figure - Sensitivity
results_filename = "parameter_sweep_results.csv"
savename = "Fig_Sensitivity.png"
# =============================================================================#
sns.set_style('white')
colors = sns.color_palette('colorblind')

sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

# Import results
df = pd.read_csv(results_filename)

# Prepare results for plotting
# Create series for plantType
# df = df.assign(plantType=df.sheetname)
# df.loc[(df.plantType == 'OCGT_Batt'), 'plantType'] = 'OCGT'
# df.loc[(df.plantType == 'CCGT_Batt'), 'plantType'] = 'CCGT'
# df.loc[(df.plantType == 'sCO2_Batt'), 'plantType'] = 'sCO2'

# Create Plots
f, a = plt.subplots(3, 5)  # ,sharex=True, sharey=True
a = a.ravel()

for idx, ax in enumerate(a):

    # Y-Variable (Vary by row)
    if idx == 0 or idx == 1 or idx == 2 or idx == 3 or idx == 4:
        y_var = 'RTE'
        y_label = 'Efficiency (%)'
        y_convert = [100.]
        ylims = [50, 100]
    elif idx == 5 or idx == 6 or idx == 7 or idx == 8 or idx == 9:
        y_var = 'kW_out_avg'
        y_label = 'Power (MW)'
        y_convert = [1.0 / 1000.0]
        ylims = [0, 60]
    elif idx == 10 or idx == 11 or idx == 12 or idx == 13 or idx == 14:
        y_var = 'kWh_out'
        y_label = 'Energy (GWh)'
        y_convert = [1.0 / 1000.0 / 1000.0]
        ylims = [0, 60]

    # X-Variable (vary by column)
    if idx == 0 or idx == 5 or idx == 10:
        # X variables
        x_var = 'depth'
        x_label = 'Depth (m)'
        x_convert = [1.0]
        xlims = [1000, 2000]
        xticks = [1200, 1500, 1800]  # Leave empty if unused
    #        xtick_labels =  []

    elif idx == 1 or idx == 6 or idx == 11:
        x_var = 'h'
        x_label = 'Thickness (m)'
        x_convert = [1.0]
        xlims = [30, 1100]
        xticks = [50, 500, 1000]
    #        xtick_labels =  ['30','75','110']

    elif idx == 2 or idx == 7 or idx == 12:
        x_var = 'phi'
        x_label = 'Porosity (-)'
        x_convert = [1.0]
        xlims = [0.2, 0.4]
        xticks = (0.25, 0.3, 0.35)
    #        xtick_labels =  ('30','75','110')

    elif idx == 3 or idx == 8 or idx == 13:
        x_var = 'm_dot'
        x_label = 'Mass flow (kg/s)'
        x_convert = [1.0]
        xlims = [125, 325]
        xticks = (100, 200, 300)
    #        xtick_labels =  ('30','75','110')

    elif idx == 4 or idx == 9 or idx == 14:
        x_var = 'r_f'
        x_label = 'Radius (m)'
        x_convert = [1.0]
        xlims = [75, 525]
        xticks = (100, 300, 500)
    #        xtick_labels =  ('30','75','110')

    #  Configurations
    plantTypes = ['sCO2', 'sCO2', 'sCO2']
    battSizes = [0.0, 0.0, 30.0]
    pct_solars = [1.0, 63.0, 63.0]
    # Corresponding labels, colors, and marker size
    labels = ['1% Solar w/o Batt', '63% Solar w/o Batt', '63% Solar 30.0 MWh Batt']
    dot_colors = [colors[0], colors[2], colors[1]]
    markers = ['o', 'x', '+']

    # Plot
    x = df.loc[:, x_var] * x_convert
    y = df.loc[:, y_var] * y_convert
    ax.scatter(x.values, y.values)

    # Despine and remove ticks
    sns.despine(ax=ax, )
    ax.tick_params(top=False, right=False)

    # # Plot by configuration
    # for plantType, battSize, pct_solar, label, dot_color, marker in zip(plantTypes, battSizes, pct_solars, labels,
    #                                                                     dot_colors, markers):
    #     # Select entries of interest
    #     df2 = df[(df.plantType == plantType) & (df.pct_solar == pct_solar) & (df.battSize_MW == battSize)]
    #
    #     # Plot
    #     x = df2.loc[:, x_var] * x_convert
    #     y = df2.loc[:, y_var] * y_convert
    #     ax.scatter(x.values, y.values, c=dot_color, marker=marker, label=label)

    # Set X and Y Limits
    ax.set_xlim(left=xlims[0], right=xlims[1])
    #    ax.set_ylim(bottom=ylims[0],top=ylims[1])

    if len(xticks) > 2:
        ax.xaxis.set_ticks(xticks)
    #        ax.set_xticks(xticks)
    #        ax.set_xticklabels = xtick_labels

    # X-axis Labels (Only bottom)
    if idx == 10 or idx == 11 or idx == 12 or idx == 13 or idx == 14:
        ax.set_xlabel(x_label)
    else:
        ax.get_xaxis().set_visible(False)

    # Y-axis labels (Only left side)
    if idx == 0 or idx == 5 or idx==10:
        ax.set_ylabel(y_label)
        ax.yaxis.set_label_coords(-0.25, 0.5)
    else:
        ax.get_yaxis().set_visible(False)

    # Legend (only for middle bottom)
    # if idx == 4:
    #            ax.legend(bbox_to_anchor=(2.6, -0.4),ncol=3)
        # ax.legend(bbox_to_anchor=(2.2, -0.2), ncol=3, prop={'size': 12})

    # Caption labels
    # caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G','']
    # plt.text(0.1, 0.9, caption_labels[idx], horizontalalignment='center', verticalalignment='center',
    #          transform=ax.transAxes, fontsize='medium', fontweight='bold')

# Adjust layout
plt.tight_layout()

# Save Figure
plt.savefig(savename, dpi=DPI, bbox_inches="tight")
plt.close()
