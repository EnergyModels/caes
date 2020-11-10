# General imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.lines as mlines

# Set Color Palette
colors = sns.color_palette("colorblind")
# Set resolution for saving figures
DPI = 300

# Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
# Single column: 90mm = 3.54 in
# 1.5 column: 140 mm = 5.51 in
# 2 column: 190 mm = 7.48 i
width = 7.48  # inches
height = 5.5  # inches

# %%=============================================================================#
# Figure 6 - LCOE
results_filename = "combined_results.csv"
savename = "Fig_comparison.png"
# =============================================================================#
case_dict = {'best_case': 'Best (n=1.04)', 'expected_case': 'Expected (n=1.1)', 'worst_case': 'Worst (n=1.21)'}

y_var = "RTE"
y_label = "Efficiency (%)"
y_convert = 100.0
y_limit = []

palette = sns.color_palette('colorblind')
colors = [palette[2],palette[0],palette[1]]

df = pd.read_csv(results_filename)
for case in case_dict.keys():
    ind = df.loc[:, 'case'] == case
    df.loc[ind, 'Case (Polytropic index)'] = case_dict[case]

# convert y_var
df.loc[:, y_var] = df.loc[:, y_var] * y_convert

df = df.fillna(0.0)

f, a = plt.subplots(1, 1)

# Set size
f.set_size_inches(width, height)

sns.histplot(data=df, x=y_var, ax=a, hue='Case (Polytropic index)', multiple='dodge', element='step', fill=False,
             legend=True,
             palette=colors, hue_order=case_dict.values())
a.set_xlabel(y_label)
a.set_xlim(left=0.0, right=100.0)

# Save Figure
plt.savefig(savename, dpi=DPI)
