from caes import sopher_method
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function

# fixed inputs
r_w = 0.265  # [m]
h = 40.0  # m
T = 298.15  # [K]
Z = 1.0  # [-]

# variables
m_dots = np.arange(1, 300, 1)  # [kg/s]
p_fs = [14.02, 17.34]  # [MPa]
ks = [50, 100, 200, 300, 500]  # [mD] (range based on Sopher et al)
r_fs = [250, 500]  # [m]

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
                delta_p = sopher_method(Q=Q, p_f=p_f, r_f=r_f, r_w=r_w, k=k, h=h, mu=mu, T=T, Z=Z)

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
                 row='Air radius [m]', col='Air pressure, p3 [MPa]', legend='full',
                 palette='colorblind', kind='line')
# ax.set_xlabel('Flow rate [kg/s]')
# ax.set_ylabel('Pressure drop [MPa]')
ax.set_titles(row_template = '{row_name}', col_template = '{col_name}')
plt.savefig('delta_p.png', dpi=300)
plt.close()
