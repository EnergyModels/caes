import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

df = pd.read_csv('all_analysis.csv')

# f, a = plt.subplots(2,1)
# a = a.ravel()
#
# sns.scatterplot(data=df, x='NEAR_DIST',y='feasible_fr', hue='NEAR_FC', ax=a[0])
#
# sns.scatterplot(data=df, x='NEAR_DIST',y='RASTERVALU', hue='NEAR_FC', ax=a[1])

# conversions and column renaming
df.loc[:, 'Distance to shore (km)'] = df.loc[:, 'NEAR_DIST'] / 1000.0
df.loc[:, 'Water depth (m)'] = df.loc[:, 'RASTERVALU']
df.loc[:, 'Feasibility (%)'] = df.loc[:, 'feasible_fr'] * 100.0
df.loc[:, 'Formation (-)'] = df.loc[:, 'formation']
df.loc[:, 'Nearest State (-)'] = df.loc[:, 'NEAR_FC']

loc_dict = {'VA_shore': 'Virginia', 'MD_shore': 'Maryland', 'NJ_shore': 'New Jersey', 'DE_shore': 'Delaware',
            'NY_shore': 'New York', 'MA_shore': 'Massachusetts', 'RI_shore': 'Rhode Island'}

formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}

# rename
for loc in df.loc[:, 'Nearest State (-)'].unique():
    ind = df.loc[:, 'Nearest State (-)'] == loc
    df.loc[ind, 'Nearest State (-)'] = loc_dict[loc]

# rename
for formation in df.loc[:, 'Formation (-)'].unique():
    ind = df.loc[:, 'Formation (-)'] == formation
    df.loc[ind, 'Formation (-)'] = formation_dict[formation]

# Filter data with feasibility greater than 0.8
# df = df[df.loc[:,'Feasibility (%)']>=0.8]

# Filter data with mean RTE greater than 0.5
df = df[df.loc[:, 'RTE_mean'] >= 0.5]

# sns.scatterplot(data=df, x='Distance to shore (km)', y='Water depth (m)', hue='Nearest State (-)',
#                 size='Feasibility (%)', style='Formation (-)')
#
# # a[1].set_ylim(top=0.0,bottom=-100.0)
#
# sns.scatterplot(data=df, x='Distance to shore (km)', y='Water depth (m)', hue='Nearest State (-)',
#                 size='Feasibility (%)', style='Formation (-)', ax=a[1])
#
# a[1].set_xlim(left=0.0,right=100.0)
# a[1].set_ylim(top=0.0,bottom=-100.0)


# create figure
f, a = plt.subplots(1, 1)
axins = zoomed_inset_axes(a, zoom=2.2, loc='upper center', bbox_to_anchor=(0.5, -0.2), bbox_transform=a.transAxes)

# Main plot
sns.scatterplot(data=df, x='Distance to shore (km)', y='Water depth (m)', hue='Nearest State (-)',
                style='Formation (-)', ax=a)

a.set_xlim(left=0.0, right=300.0)
a.set_ylim(top=0, bottom=-400.0)
# a.set_yscale('symlog')

# Inset


x_lims = [0.0, 100.0]
y_lims = [0, -60.0]

rect = plt.Rectangle((x_lims[0] + 1, y_lims[0]), x_lims[1] - x_lims[0] + 1, y_lims[1] - y_lims[0], fill=False,
                     facecolor="black",
                     edgecolor='black', linestyle='--')

a.add_patch(rect)

sns.scatterplot(data=df, x='Distance to shore (km)', y='Water depth (m)', hue='Nearest State (-)',
                style='Formation (-)', legend=False, ax=axins)

axins.set_xlim(left=x_lims[0], right=x_lims[1])
axins.set_ylim(top=y_lims[0], bottom=y_lims[1])
# axins.set_yscale('symlog')
axins.yaxis.set_major_locator(plt.MaxNLocator(3))

a.legend(bbox_to_anchor=(1.025, 0.0), loc="center left", ncol=1)

a.text(-0.1, 1.0, 'a', horizontalalignment='center', verticalalignment='center',
       transform=a.transAxes, fontsize='medium', fontweight='bold')

axins.text(-0.3, 1.0, 'b', horizontalalignment='center', verticalalignment='center',
           transform=axins.transAxes, fontsize='medium', fontweight='bold')

# Add rectangle that represents subplot2


# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 7.0  # inches

# Set size
f.set_size_inches(width, height)
plt.subplots_adjust(top=0.95,
                    bottom=0.5,
                    left=0.12,
                    right=0.7,
                    hspace=0.2,
                    wspace=0.2)
# save
plt.savefig('FigS3_Distance_v_Depth_By_State.png', dpi=300)
