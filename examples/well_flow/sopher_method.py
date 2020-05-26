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
m_dots = np.arange(1, 100, 1)  # [m3/s]
p_fs = [10.0, 22.0]  # [MPa]
ks = [50, 100, 200, 300, 500]  # [mD] (range based on Sopher et al)
r_fs = [250, 500]  # [m]

Vs = [5.88e5]

attributes = ['Q', 'p_in', 'r_f', 'r_w', 'k', 'h', 'mu', 'T', 'Z',  'm_dot', 'delta_p', 'rho']
df = pd.DataFrame(columns=attributes)

for p_f in p_fs:

    if p_f == 10.0:
        rho = CP.PropsSI('D', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')  # [kg/m3] inputs are degrees K and Pa
        mu = CP.PropsSI('V', 'T', T, 'P', p_f * 1e6, 'AIR.MIX') * 1000  # convert Pa*s (output) to cP
        Z = CP.PropsSI('Z', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')

    else:  # p_f == 22.0:
        rho = CP.PropsSI('D', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')
        mu = CP.PropsSI('V', 'T', T, 'P', p_f * 1e6, 'AIR.MIX') * 1000
        Z = CP.PropsSI('Z', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')

    for r_f in r_fs:

        for k in ks:
            for m_dot in m_dots:
                Q = m_dot / rho
                delta_p = sopher_method(Q=Q, p_f=p_f, r_f=r_f, r_w=r_w, k=k, h=h, mu=mu, T=T, Z=Z)

                s = pd.Series(index=attributes)
                s['Q'] = Q
                s['p_in'] = p_f
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

sns.set_context('talk')
ax = sns.relplot(x='m_dot', y='delta_p', hue='k', data=df, row='r_f', col='p_in', legend='full', palette='colorblind')
# ax.set_xlabel('Flow rate [kg/s]')
# ax.set_ylabel('Pressure drop [MPa]')
plt.savefig('delta_p.png', dpi=300)
plt.close()
