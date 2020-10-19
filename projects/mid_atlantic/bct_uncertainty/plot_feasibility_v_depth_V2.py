# Import libraries (requires: pandas, seaborn, matplotlib, xlrd)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset


# ******************************
# Inputs
# ******************************

# VARIABLES TO CHANGE GRAPH
dpi = 1000
context = "notebook"
style = "whitegrid"
color_pal = sns.color_palette("colorblind")

states = ['Virginia', 'Maryland', 'New Jersey', 'Delaware', 'New York', 'Massachusetts', 'Rhode Island']
colors = [color_pal[5], color_pal[4], color_pal[7], color_pal[3], color_pal[2], color_pal[1], color_pal[0]]

formations = ['LK1', 'MK1-3', 'UJ1']
markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'o', 'X']

formation_dict = {'LK1': 'Lower Cretaceous', 'MK1-3': 'Middle Cretaceous', 'UJ1': 'Upper Jurassic'}


dot_size = 100
marker_size = 10
markeredgewidth = 2

# ******************************
# Prepare Data
# ******************************

# Read-in results file and convert
df = pd.read_csv('all_analysis.csv')

# conversions and column renaming
df.loc[:, 'Distance to shore (km)'] = df.loc[:, 'NEAR_DIST'] / 1000.0
df.loc[:, 'Water depth (m)'] = df.loc[:, 'RASTERVALU']
df.loc[:, 'Feasibility (%)'] = df.loc[:, 'feasible_fr'] * 100.0
df.loc[:, 'Formation (-)'] = df.loc[:, 'formation']
df.loc[:, 'Nearest State (-)'] = df.loc[:, 'NEAR_FC']

df_loc = {'VA_shore': 'Virginia', 'MD_shore': 'Maryland', 'NJ_shore': 'New Jersey', 'DE_shore': 'Delaware',
          'NY_shore': 'New York', 'MA_shore': 'Massachusetts', 'RI_shore': 'Rhode Island'}

# rename
for loc in df.loc[:, 'Nearest State (-)'].unique():
    ind = df.loc[:, 'Nearest State (-)'] == loc
    df.loc[ind, 'Nearest State (-)'] = df_loc[loc]

# Plot
savename = "Fig8_Distance_vs_depth.png"
# ******************************

x_var = 'Distance to shore (km)'
x_label = 'Distance to shore (km)'
x_convert = 1.0
x_lims0 = [0.0, 300.0]
x_lims1 = [0.0, 100.0]

y_var = 'Water depth (m)'
y_label = 'Water depth (m)'
y_convert = 1.0
y_lims0 = [-3000.0, 0.0]
y_lims1 = [-100.000, 0.0]

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 7.0  # inches

# create figure
f, a = plt.subplots(1, 1)

# create inset
# axins = zoomed_inset_axes(a, zoom=1.5, loc='lower right')
axins = zoomed_inset_axes(a, zoom=1.5, loc='lower right', bbox_to_anchor=(0.975, 0.1), bbox_transform=a.transAxes)

sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("paper")
sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

markeredgewidth = 1.5
elinewidth = 1.0

# Iterate through subplots
for i in range(2):

	if i == 0:
		ax = a
	else:
		ax = axins

	# Iterate through plant types
	for state, color in zip(states, colors):

		# Iterate through capture technologies
		for formation, marker in zip(formations, markers):

			# Select entries of interest

			df2 = df[(df.loc[:,'Nearest State (-)'] == state) & (df.formation == formation)]

			x = list(df2.loc[:, 'Distance to shore (km)'] * x_convert)
			y = list(df2.loc[:, 'Water depth (m)'] * y_convert)
			s = df2.loc[:, 'Feasibility (%)']

			# Plot Data
			ax.plot(x, y, linestyle='', marker=marker, markersize=s, markeredgewidth=markeredgewidth, markeredgecolor=color, markerfacecolor=color)

	# Despine and remove ticks
	if i == 0:
		sns.despine(ax=ax, )
		ax.tick_params(top=False, right=False)

	# Labels
	if i == 0:
		ax.set_xlabel(x_label)
		ax.set_ylabel(y_label)

	# Axis Limits
	if i == 0:
		if len(x_lims0) == 2:
			ax.set_xlim(left=x_lims0[0], right=x_lims0[1])
		if len(y_lims0) == 2:
			ax.set_ylim(bottom=y_lims0[0], top=y_lims0[1])
	elif i == 1:
		if len(x_lims1) == 2:
			ax.set_xlim(left=x_lims1[0], right=x_lims1[1])
		if len(x_lims1) == 2:
			ax.set_ylim(bottom=y_lims1[0], top=y_lims1[1])

	# Caption labels
	caption_labels = ['A', 'B', 'C', 'D', 'E', 'F']
	if i==0:
		ax.text(0.025, 0.975, caption_labels[i], horizontalalignment='center', verticalalignment='center',
			transform=ax.transAxes, fontsize='medium', fontweight='bold')
	elif i==1:
		ax.text(0.05, 0.9, caption_labels[i], horizontalalignment='center', verticalalignment='center',
				transform=ax.transAxes, fontsize='medium', fontweight='bold')


# Set size
f = plt.gcf()
f.set_size_inches(width, height)

# Add rectangle that represents subplot2
rect = plt.Rectangle((x_lims1[0], y_lims1[0]), x_lims1[1] - x_lims1[0], y_lims1[1] - y_lims1[0], facecolor="black",
					 alpha=0.05)
# rect = plt.Rectangle((x_lims1[0], y_lims1[0]), x_lims1[1] - x_lims1[0], y_lims1[1] - y_lims1[0], edgecolor='black',
#                      facecolor='None', )

a.add_patch(rect)
a.text(x_lims1[1], y_lims1[0], 'Extent of B', horizontalalignment='right', verticalalignment='top', rotation=0)

# Legend
# Iterate through plant technologies
patches = []
for state, color in zip(states, colors):
	patches.append(mpatches.Patch(color=color, label=state))

leg1 = a.legend(handles=patches, bbox_to_anchor=(0.15, -0.11), loc="upper left", title='Nearest State (-)', ncol=1)

# Iterate through capture technologies
symbols = []
for formation, marker in zip(formations, markers):
	symbols.append(mlines.Line2D([], [], color='black', linestyle='', marker=marker, markersize=9,
								 markerfacecolor='None', markeredgewidth=1.5,
								 label=formation_dict[formation]))
leg2 = a.legend(handles=symbols, bbox_to_anchor=(0.4575, -0.11), loc="upper left", title='Technology', ncol=1)

# w0 = a.get_window_extent().width
# w1 = leg1.get_window_extent().width / w0
# w2 = leg2.get_window_extent().width / w0
# w3 = leg2.get_window_extent().width / w0
# w = (0.5 * (w0 - w1 - w2) + w1)/w0

# Pre/Post
#patches2 = [mpatches.Patch(edgecolor='black', facecolor='None', label='Pre'),
#			mpatches.Patch(edgecolor='black', facecolor='black', label='Post')]
#leg3 = a.legend(handles=patches2, bbox_to_anchor=(0.65, -0.11), loc="upper left", title='Capture Type')

a.add_artist(leg1)
a.add_artist(leg2)
# a.add_artist(leg3)
# plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=12)
# plt.tight_layout()
plt.subplots_adjust(top=0.95,
					bottom=0.335,
					left=0.11,
					right=0.95,
					hspace=0.2,
					wspace=0.2)
# plt.savefig(savename, dpi=dpi, bbox_extra_artists=(leg1, leg2, leg3))
plt.savefig(savename, dpi=dpi, bbox_extra_artists=(leg1, leg2))
# plt.savefig(savename, dpi=dpi)