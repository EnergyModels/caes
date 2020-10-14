import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines

# =============================== #
# common inputs
# =============================== #
results_filename = "study_results.csv"

# Set Color Palette
pal = "colorblind"

# Set resolution for saving figures
DPI = 300

# result variable
y_var = "RTE"
y_label = "Efficiency (%)"
y_convert = 100.0
y_limit = []

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 5.5  # inches

duration_dict = {10: '10 hour', 24: '24 hour', 168: '168 hour'}
capacity_dict = {50: '50 MW', 100: '100 MW', 150: '150 MW', 200: '200 MW', 250: '250 MW'}
formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}

# =============================== #
# process data
# =============================== #
# read data
df = pd.read_csv(results_filename)
# replace nan with 0.0
df = df.fillna(0.0)

# =============================== #
# version 1
savename = "Fig6_sizing_cdf_v1.png"
# =============================== #

# create figure
n_rows = len(df.sheet_name.unique())
n_cols = len(df.duration_hr.unique())
f, a = plt.subplots(n_rows, n_cols, sharey=True, sharex=True, squeeze=False)
# a = a.ravel()

# # Set size
f.set_size_inches(width, height)

for i, formation in enumerate(df.sheet_name.unique()):
    for j, duration in enumerate(df.duration_hr.unique()):
        ax = a[i, j]
        df2 = df[(df.loc[:, "duration_hr"] == duration) & (df.loc[:, "sheet_name"] == formation)]
        df2.loc[:, y_var] = df2.loc[:, y_var] * y_convert
        sns.ecdfplot(data=df2, x=y_var, ax=ax, hue="capacity_MW", legend=False, palette=pal)

        ax.set_xlim(left=50.0, right=100.0)

        if i == n_rows - 1:
            ax.set_xlabel(y_label)

        # top labels
        if i == 0:
            plt.text(0.5, 1.1, duration_dict[duration], horizontalalignment='center', verticalalignment='center',
                     transform=ax.transAxes, fontsize='medium', fontweight='bold')

        # side labels
        if j == n_cols - 1:
            plt.text(1.1, 0.5, formation, horizontalalignment='center', verticalalignment='center',
                     transform=ax.transAxes, fontsize='medium', fontweight='bold')

# Save Figure
plt.savefig(savename, dpi=DPI)
# plt.close()

# =============================== #
# version 2
savename = "Fig6_sizing_cdf_v2.png"
# =============================== #

# create figure
n_rows = len(df.sheet_name.unique())
n_cols = len(df.capacity_MW.unique())
f, a = plt.subplots(n_rows, n_cols, sharey=True, sharex=True, squeeze=False)
# a = a.ravel()

# # Set size
f.set_size_inches(width, height)

for i, formation in enumerate(df.sheet_name.unique()):
    for j, capacity in enumerate(df.capacity_MW.unique()):
        ax = a[i, j]
        df2 = df[(df.loc[:, "capacity_MW"] == capacity) & (df.loc[:, "sheet_name"] == formation)]
        df2.loc[:, y_var] = df2.loc[:, y_var] * y_convert
        sns.ecdfplot(data=df2, x=y_var, ax=ax, hue="duration_hr", legend=False, palette=pal)

        ax.set_xlim(left=50.0, right=100.0)

        if i == n_rows - 1:
            ax.set_xlabel(y_label)

        # top labels
        if i == 0:
            plt.text(0.5, 1.1, capacity_dict[capacity], horizontalalignment='center', verticalalignment='center',
                     transform=ax.transAxes, fontsize='medium', fontweight='bold')

        # side labels
        if j == n_cols - 1:
            plt.text(1.1, 0.5, formation, horizontalalignment='center', verticalalignment='center',
                     transform=ax.transAxes, fontsize='medium', fontweight='bold')

# Save Figure
plt.savefig(savename, dpi=DPI)
# plt.close()

# =============================== #
# version 3
savename = "Fig6_sizing_cdf_v3.png"
# =============================== #
# create figure
n_rows = 1
n_cols = len(df.sheet_name.unique())
f, a = plt.subplots(n_rows, n_cols, sharey=True, sharex=True, squeeze=False)

# # Set size
width = 7.48  # inches
height = 5.5  # inches
f.set_size_inches(width, height)

duration = 24

formations = ['MK1-3', 'LK1', 'UJ1']

for j, formation in enumerate(formations):  # df.sheet_name.unique()):
    ax = a[0, j]
    df2 = df[(df.loc[:, "duration_hr"] == duration) & (df.loc[:, "sheet_name"] == formation)]
    df2.loc[:, y_var] = df2.loc[:, y_var] * y_convert

    if j == 1:
        leg = True
    else:
        leg = False

    df2.loc[:, 'Capacity (MW)'] = df2.loc[:, 'capacity_MW']
    sns.ecdfplot(data=df2, x=y_var, ax=ax, hue="Capacity (MW)", legend=leg, palette=pal)

    ax.set_xlim(left=50.0, right=90.0)

    if j == 0:
        ax.set_ylabel('Probability (-)')

    if j == 1:
        ax.set_xlabel('Round-Trip Efficiency (%)')
        # ax.legend(bbox_to_anchor=(0.5, -0.3), ncol=5)
    else:
        ax.set_xlabel('')

    # top labels
    plt.text(0.5, 1.05, formation_dict[formation], horizontalalignment='center', verticalalignment='center',
             transform=ax.transAxes, fontsize='medium', fontweight='bold')

lines = []
for capacity, color in zip(df.capacity_MW.unique(), sns.color_palette(pal)):
    lines.append(mlines.Line2D([], [], color=color, linestyle='-', marker='None', markersize=9,
                               markerfacecolor='None', markeredgewidth=1.5,
                               label=capacity))
a[0, 1].legend(handles=lines, bbox_to_anchor=(0.5, -0.15), loc="upper center", title='Capacity (MW)', ncol=5)

plt.subplots_adjust(top=0.88, bottom=0.23, left=0.1,right=0.9,hspace=0.205,wspace=0.2)

# Save Figure
plt.savefig(savename, dpi=DPI)
# plt.close()

# # =============================== #
# # version 4
# savename = "Fig6_sizing_cdf_v4.png"
# # =============================== #
# # create figure
# n_rows = 1
# n_cols = len(df.duration_hr.unique())
# f, a = plt.subplots(n_rows, n_cols, sharey=True, sharex=True, squeeze=False)
#
# # # Set size
# f.set_size_inches(width, height)
#
# for j, duration in enumerate(df.duration_hr.unique()):
#     ax = a[0, j]
#     df2 = df[(df.loc[:, "duration_hr"] == duration)]
#     df2.loc[:, y_var] = df2.loc[:, y_var] * y_convert
#     sns.ecdfplot(data=df2, x=y_var, ax=ax, hue="capacity_MW", legend=False, palette=pal)
#
#     ax.set_xlim(left=50.0, right=100.0)
#
#     ax.set_xlabel(y_label)
#
#     # top labels
#     plt.text(0.5, 1.1, duration_dict[duration], horizontalalignment='center', verticalalignment='center',
#              transform=ax.transAxes, fontsize='medium', fontweight='bold')
#
# # Save Figure
# plt.savefig(savename, dpi=DPI)
# # plt.close()
