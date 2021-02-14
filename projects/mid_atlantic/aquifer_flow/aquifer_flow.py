from caes import aquifer_dp
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
import matplotlib.lines as mlines

# fixed inputs
r_w = 0.41 / 2.0  # [m]
h = 50.0  # m
T = 35.0 + 273.15  # [K]
Z = 1.0  # [-]

# variables
m_dots = np.arange(1, 400, 1)  # [kg/s]
p_fs = [12.0]  # [MPa]
ks = [2.0, 5.0, 10.0, 50.0, 100.0]  # [mD] (range based on Sopher et al. 2019)
r_fs = [100]  # [m]

attributes = ['Q', 'p_f', 'r_f', 'r_w', 'k', 'h', 'mu', 'T', 'Z', 'm_dot', 'delta_p', 'rho']
df = pd.DataFrame(columns=attributes)

for p_f in p_fs:

    rho = CP.PropsSI('D', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')  # [kg/m3] inputs are degrees K and Pa
    mu = CP.PropsSI('V', 'T', T, 'P', p_f * 1e6, 'AIR.MIX') * 1000  # convert Pa*s (output) to cP
    Z = CP.PropsSI('Z', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')

    for r_f in r_fs:

        for k in ks:
            for m_dot in m_dots:
                Q = m_dot / rho
                delta_p = aquifer_dp(Q=Q, p_f=p_f, r_f=r_f, r_w=r_w, k=k, h=h, mu=mu, T=T, Z=Z)

                s = pd.Series(index=attributes)
                s['Q'] = Q
                s['p_f'] = p_f
                s['r_f'] = r_f
                s['r_w'] = r_w
                s['k'] = k
                s['h'] = h
                s['mu'] = mu
                s['T'] = T
                s['Z'] = Z

                s['delta_p'] = delta_p
                s['m_dot'] = m_dot
                s['rho'] = rho

                df = df.append(s, ignore_index=True)

# rename columns for plotting
df['Mass flow [kg/s]'] = df['m_dot']
df['Pressure drop [MPa]'] = df['delta_p']
df['Permeability [mD]'] = df['k']
df['Air radius [m]'] = df['r_f']
df['Air pressure, p3 [MPa]'] = df['p_f']
df.to_csv('results.csv')

sns.set_context('talk')
ax = sns.relplot(x='Mass flow [kg/s]', y='Pressure drop [MPa]', hue='Permeability [mD]', data=df,
                 legend=False,
                 palette='colorblind', kind='line')
# ax.set_xlabel('Flow rate [kg/s]')
# ax.set_ylabel('Pressure drop [MPa]')
ax.set_titles(row_template='{row_name}', col_template='{col_name}')

# patches = []
# for plantType, plant_color in zip(plantTypes, plant_colors):
#     patches.append(mpatches.Patch(color=plant_color, label=label_dict[plantType]))

ax.axes[0][0].set_ylim(top=12)

lines = []
colors = sns.color_palette('colorblind')
entries = ks
for entry, color in zip(entries, colors):
    lines.append(mlines.Line2D([], [], color=color, linestyle='-', marker='', markersize=9,
                               markerfacecolor='None', markeredgewidth=0.0, label=entry))

plt.legend(handles=lines, loc="upper left", title='Permeability\n[mD]')

plt.tight_layout()
plt.savefig('FigS1_aquifer_delta_p.png', dpi=300)

# plt.close()
