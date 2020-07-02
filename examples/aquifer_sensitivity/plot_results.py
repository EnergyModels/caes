# %%=============================================================================#
# Figure 8 - sCO2 Sensitivity
results_filename = "results_monte_carlo.csv"
savename = "Fig8_sCO2_Sensitivity.png"
# =============================================================================#
sns.set_style('white')

# Import results
df = pd.read_csv(results_filename)

# Filter Results
df = df[(df.LCOE > 0) & (df.emissions_tons > 0)]

# Prepare results for plotting
# Create series for plantType
df = df.assign(plantType=df.sheetname)
df.loc[(df.plantType == 'OCGT_Batt'), 'plantType'] = 'OCGT'
df.loc[(df.plantType == 'CCGT_Batt'), 'plantType'] = 'CCGT'
df.loc[(df.plantType == 'sCO2_Batt'), 'plantType'] = 'sCO2'
# Create series for pct_solar
df = df.assign(pct_solar=df.solarCapacity_MW)
df.loc[(df.pct_solar == 0.635), 'pct_solar'] = 1.0
df.loc[(df.pct_solar == 32.635), 'pct_solar'] = 63.0

# Create Plots
f, a = plt.subplots(2, 3)  # ,sharex=True, sharey=True
a = a.ravel()

for idx, ax in enumerate(a):

    # Y-Variable (Vary by row)
    if idx == 0 or idx == 1 or idx == 2:
        y_var = 'fuelCost_dollars'
        y_label = 'Fuel Cost (M$)'
        y_convert = [1. / 1E6]
        ylims = [10, 18]
    elif idx == 3 or idx == 4 or idx == 5:
        y_var = 'solarCurtail_pct'
        y_label = 'Curtailment (%)'
        y_convert = [1.0]
        ylims = [0, 60]

    # X-Variable (vary by column)
    if idx == 0 or idx == 3:
        # X variables
        x_var = 'maxEfficiency'
        x_label = 'Max Efficiency (%)'
        x_convert = [1.0]
        xlims = [40, 60]
        xticks = [40, 50, 60]  # Leave empty if unused
    #        xtick_labels =  []

    elif idx == 1 or idx == 4:
        x_var = 'rampRate'
        x_label = 'Ramp Rate (%/min)'
        x_convert = [1.0]
        xlims = [30, 110]
        xticks = [30, 75, 110]
    #        xtick_labels =  ['30','75','110']
    elif idx == 2 or idx == 5:
        x_var = 'minRange'
        x_label = 'Min. Load (%)'
        x_convert = [1.0]
        xlims = [15, 60]
        xticks = (20, 40, 60)
    #        xtick_labels =  ('30','75','110')

    #  Configurations
    plantTypes = ['sCO2', 'sCO2', 'sCO2']
    battSizes = [0.0, 0.0, 30.0]
    pct_solars = [1.0, 63.0, 63.0]
    # Corresponding labels, colors, and marker size
    labels = ['1% Solar w/o Batt', '63% Solar w/o Batt', '63% Solar 30.0 MWh Batt']
    dot_colors = [colors[0], colors[2], colors[1]]
    markers = ['o', 'x', '+']

    # Plot by configuration
    for plantType, battSize, pct_solar, label, dot_color, marker in zip(plantTypes, battSizes, pct_solars, labels,
                                                                        dot_colors, markers):
        # Select entries of interest
        df2 = df[(df.plantType == plantType) & (df.pct_solar == pct_solar) & (df.battSize_MW == battSize)]

        # Plot
        x = df2.loc[:, x_var] * x_convert
        y = df2.loc[:, y_var] * y_convert
        ax.scatter(x.values, y.values, c=dot_color, marker=marker, label=label)

    # Set X and Y Limits
    ax.set_xlim(left=xlims[0], right=xlims[1])
    #    ax.set_ylim(bottom=ylims[0],top=ylims[1])

    if len(xticks) > 2:
        ax.xaxis.set_ticks(xticks)
    #        ax.set_xticks(xticks)
    #        ax.set_xticklabels = xtick_labels

    # X-axis Labels (Only bottom)
    if idx == 3 or idx == 4 or idx == 5:
        ax.set_xlabel(x_label)
    else:
        ax.get_xaxis().set_visible(False)

    # Y-axis labels (Only left side)
    if idx == 0 or idx == 3:
        ax.set_ylabel(y_label)
        ax.yaxis.set_label_coords(-0.25, 0.5)
    else:
        ax.get_yaxis().set_visible(False)

    # Legend (only for middle bottom)
    if idx == 4:
        #        ax.legend(bbox_to_anchor=(2.6, -0.4),ncol=3)
        ax.legend(bbox_to_anchor=(2.2, -0.2), ncol=3, prop={'size': 12})

    # Caption labels
    caption_labels = ['A', 'B', 'C', 'D', 'E', 'F']
    plt.text(0.1, 0.9, caption_labels[idx], horizontalalignment='center', verticalalignment='center',
             transform=ax.transAxes, fontsize='medium', fontweight='bold')

# Adjust layout
plt.tight_layout()

# Save Figure
plt.savefig(savename, dpi=DPI, bbox_inches="tight")
plt.close()