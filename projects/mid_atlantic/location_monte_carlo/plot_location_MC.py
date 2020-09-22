# General imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set Color Palette
colors = sns.color_palette("colorblind")
# Set resolution for saving figures
DPI = 1200

# %%=============================================================================#
# Figure 6 - LCOE
results_filename = "mc_results.csv"
savename = "Fig7_location_MC.png"
# =============================================================================#
y_vars = ["RTE", "duration", "kW_out_avg"]
y_labels = ["Efficiency\n(%)", "Duration\n(hr)", "Power\n(MW)"]
y_converts = [100.0, 1.0, 1e-3]
y_limits = [[], [], []]

series_var = 'sheetname'

sns.set_style('white')
# Import results
df = pd.read_csv(results_filename)
df.loc[:, 'duration'] = df.loc[:, 'kWh_out'] / df.loc[:, 'kW_out_avg']

# Create Plots
f, a = plt.subplots(3, 1, sharex=True, sharey=True)
a = a.ravel()

# Collect statistics
labels = ['plantType', 'battSize_MW', 'pct_solar', 'min', 'avg', 'max']
stats = []
variables = ['plantType', 'battSize_MW', 'pct_solar', 'min', 'avg', 'max']

for idx, ax in enumerate(a):

    # Variable Plotted
    y_var = y_vars[idx]
    y_label = y_labels[idx]
    y_convert = y_converts[idx]
    y_limit = y_limits[idx]

    # Plot
    for sheetname in df.sheetname:
        # Set Color and label
        if sheetname == 'PJM':
            color = colors[1]
            label = 'PJM'
        elif sheetname == 'NYISO':
            color = colors[0]
            label = 'NY ISO'
        else:  # elif sheetname == 'ISONE':
            color = colors[2]
            label = 'ISO New England'

        # Plot
        df2 = df[(df.sheetname == sheetname)]

        #        bin_size = 0.001; min_edge = 0.06; max_edge = 0.12
        # bin_size = 0.001;
        # min_edge = 0.03;
        # max_edge = 0.08
        # N = int((max_edge - min_edge) / bin_size);
        # Nplus1 = N + 1
        # bin_list = np.linspace(min_edge, max_edge, Nplus1)
        # ax.hist(df2.loc[:, y_var] * y_convert, label=label, color=color, bins=bin_list, histtype='step',
        #         fill=False)  # ,facecolor=False)
        ax.hist(df2.loc[:, y_var] * y_convert, label=label, color=color, histtype='step',
                fill=False)  # ,facecolor=False)

        # Collect statistics
        #        stats.append([plantType,battSize,pct_solar,df2.loc[:,y_var].min(),df2.loc[:,y_var].mean(),df2.loc[:,y_var].max()])
        # s = pd.Series(index=variables)
        # s['ISO'] = sheetname
        # s['min'] = df2.loc[:, y_var].min()
        # s['mean'] = df2.loc[:, y_var].mean()
        # s['max'] = df2.loc[:, y_var].max()
        # stats = stats.append(s, ignore_index=True)

    # Axes Labels
    # X-axis Labels (Only bottom)
    if idx == 2 or idx == 3:
        ax.set_xlabel(y_label)
    else:
        ax.get_xaxis().set_visible(False)

    # Y-Label
    if idx == 0 or idx == 2:
        ax.set_ylabel("Event Count")

    # Set Y-limits
    ax.set_ylim(top=55)

    # Additional Labels
    # if idx == 0:
    #     ax.text(0.5, 1.1, 'No Battery', horizontalalignment='center', verticalalignment='top', transform=ax.transAxes)
    # elif idx == 1:
    #     ax.text(0.5, 1.1, '30 MWh Battery', horizontalalignment='center', verticalalignment='top',
    #             transform=ax.transAxes)
    #     ax.text(1.1, 0.5, '1% Solar', horizontalalignment='center', verticalalignment='center',
    #             rotation=270, transform=ax.transAxes)
    # elif idx == 3:
    #     ax.text(1.1, 0.5, '63% Solar', horizontalalignment='center', verticalalignment='center',
    #             rotation=270, transform=ax.transAxes)

    # Legend
    #    ax.legend()

    # Caption labels
    caption_labels = ['A', 'B', 'C', 'D', 'E', 'F']
    plt.text(0.1, 0.9, caption_labels[idx], horizontalalignment='center', verticalalignment='center',
             transform=ax.transAxes, fontsize='medium', fontweight='bold')

# Adjust layout
plt.tight_layout()

a[2].legend(bbox_to_anchor=(1.75, -0.3), ncol=3)
# Adjust layout
plt.tight_layout()

# Save Figure
plt.savefig(savename, dpi=DPI, bbox_inches="tight")
plt.close()

# Collect statistics
df_stats = pd.DataFrame(stats)
df_stats.to_csv('stats.csv')
