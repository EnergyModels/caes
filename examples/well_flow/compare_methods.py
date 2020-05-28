from caes import sopher_method, confined_flow, unconfined_flow
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function

# fixed inputs
r_w = 0.265  # [m]
h = 40.0  # m
r_f = 500  # [m]
T = 298.15  # [K]

# variables
p_fs = [10.0, 22.0]  # [MPa]
ks = [100, 500]  # [mD] (range based on Sopher et al)
m_dots = np.arange(1, 100, 1)  # [m3/s]

attributes = ['Q', 'r_f', 'r_w', 'k', 'mu', 'h', 'p_f', 'T', 'Z', 'm_dot', 'rho',  # inputs
              'method', 'delta_p']  # results
df = pd.DataFrame(columns=attributes)

methods = ['sopher', 'confined', 'unconfined']
for p_f in p_fs:

    rho = CP.PropsSI('D', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')  # [kg/m3] inputs are degrees K and Pa
    mu = CP.PropsSI('V', 'T', T, 'P', p_f * 1e6, 'AIR.MIX') * 1000  # convert Pa*s (output) to cP
    Z = CP.PropsSI('Z', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')

    for k in ks:
        for m_dot in m_dots:
            Q = m_dot / rho
            for method in methods:
                if method == 'sopher':
                    delta_p = sopher_method(Q=Q, r_f=r_f, r_w=r_w, k=k, mu=mu, h=h, p_f=p_f, T=T, Z=Z)
                elif method == 'confined':
                    delta_p = confined_flow(Q=Q, r_f=r_f, r_w=r_w, k=k, mu=mu, h=h, )
                else:  # method == 'unconfined':
                    delta_p = unconfined_flow(Q=Q, r_f=r_f, r_w=r_w, k=k, mu=mu, p_f=p_f, rho=rho)

                s = pd.Series(index=attributes)
                s['Q'] = Q
                s['r_f'] = r_f
                s['r_w'] = r_w
                s['k'] = k
                s['mu'] = mu
                s['h'] = h
                s['p_f'] = p_f
                s['T'] = T
                s['Z'] = Z
                s['m_dot'] = m_dot
                s['rho'] = rho

                s['method'] = method
                s['delta_p'] = delta_p

                df = df.append(s, ignore_index=True)

sns.set_context('talk')
ax = sns.relplot(x='m_dot', y='delta_p', hue='method', data=df, row='k', col='p_f', legend='full', palette='colorblind')
# ax.set_xlabel('Flow rate [kg/s]')
# ax.set_ylabel('Pressure drop [MPa]')
plt.savefig('method_comparison1.png', dpi=300)
plt.close()


df2 = df.loc[df.loc[:,'method']!='confined',:]
sns.set_context('talk')
ax = sns.relplot(x='m_dot', y='delta_p', hue='method', data=df2, row='k', col='p_f', legend='full', palette='colorblind')
# ax.set_xlabel('Flow rate [kg/s]')
# ax.set_ylabel('Pressure drop [MPa]')
plt.savefig('method_comparison2.png', dpi=300)
plt.close()