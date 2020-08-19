import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================
# user inputs
# =====================================
# data input
results_filename = "mc_results.csv"
sheetnames = ['fixed_diameter', 'geophysical']
savenames = ["Fig_general_MC_fixed_diameter.png", "Fig_general_MC_geophysical.png"]

# figure resolution
DPI = 400  # Set resolution for saving figures

x_vars = ["phi", "k", "depth", "h", "m_dot", "r_f"]
x_labels = ["Porosity\n(-)", "Permeability\n(mD)", "Depth\n(m)", "Thickness\n(m)",
            "Mass flow rate\n(kg/s)", "Formation radius\n(m)"]
x_converts = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
x_limits = [[], [], [], [], [], []]

y_vars = ["RTE", "kW_out_avg", "duration"]
y_labels = ["Efficiency\n(%)", "Power\n(MW)", "Storage Duration\n(hr)"]
y_converts = [100.0, 1e-3, 1.0]
y_limits = [[], [], []]

series_var = 'm_dot'
series_convert = 1.0
series_label = "Mass flow (kg/s)"

# =====================================
# process data
# =====================================

# Import results
df_all = pd.read_csv(results_filename)

# Filter Results with errors
df_all = df_all[df_all.errors == False]

# create new entry called duration
df_all.loc[:, 'duration'] = df_all.loc[:, 'kWh_out'] / df_all.loc[:, 'kW_out_avg']

for sheetname, savename in zip(sheetnames, savenames):
    # select only data with the specified sheetname
    df = df_all[df_all.sheetname == sheetname]

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
    colors = sns.color_palette("colorblind")

    count = 0
    # iterate through x-variables
    for i, (x_var, x_label, x_convert, x_limit) in enumerate(zip(x_vars, x_labels, x_converts, x_limits)):

        # iterate through y-variables
        for j, (y_var, y_label, y_convert, y_limit) in enumerate(zip(y_vars, y_labels, y_converts, y_limits)):

            # access subplot
            ax = a[j, i]

            # get data and convert
            x = x_convert * df.loc[:, x_var]
            y = y_convert * df.loc[:, y_var]
            c = series_convert * df.loc[:, series_var]
            im = ax.scatter(x, y, c=c)

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
            # caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            # plt.text(0.1, 0.9, caption_labels[count], horizontalalignment='center', verticalalignment='center',
            #          transform=ax.transAxes, fontsize='medium', fontweight='bold')
            count = count + 1

    # Legend
    # y_pos = j / 2 + 0.5
    # leg = a[j, i].legend(bbox_to_anchor=(1.2, y_pos), ncol=1, loc='center')
    # x_pos = -0.1
    # leg = a[j, i].legend(bbox_to_anchor=(x_pos, -0.6), ncol=3, loc='upper center')

    # Colorbar
    cbar = f.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(series_label)

    # Adjust layout
    # plt.tight_layout()
    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.2)
    f.align_ylabels(a[:, 0])  # align y labels

    # Save Figure
    # plt.savefig(savename, dpi=DPI, bbox_extra_artists=leg)
    plt.savefig(savename, dpi=DPI)
    # plt.close()
