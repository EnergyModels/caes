from caes import friction_coeff
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import pi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# fixed inputs
T = 290  # [K]
p = 15.0  # pressures [MPa]
depth = 1420  # depth [m]
d = 0.53 * 2.0  # diameter [m]

# parameters to sweep
m_dots = np.arange(0.0, 420, 20)  # flow rates [kg/s]
epsilons = np.arange(0.002, 0.0061, 0.002) * 1.0e-3  # roughness [m]
pressures = np.arange(10.0, 15.0, 1.0)  # pressures [MPa]

# dataframe to store results
attributes = ['T', 'p', 'epsilon', 'd', 'm_dot', 'rho', 'mu',  # inputs
              'A', 'U', 'Re', 'f']  # results
df = pd.DataFrame(columns=attributes)

# perform parameter sweep
for m_dot in m_dots:
    for epsilon in epsilons:
        for p in pressures:
            # fluid properties, inputs are degrees K and Pa
            rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, "Air.mix")  # density [kg/m3]
            mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, "Air.mix")  # viscosity [Pa*s]

            # velocity
            A = pi / 4.0 * d ** 2.0  # pipe cross-sectional area [m^2]
            U = m_dot / (rho * A)  # velocity [m/s]

            # Reynolds number
            Re = rho * d * abs(U) / mu

            f = friction_coeff(Re=Re, epsilon=epsilon, d=d)

            # save results
            s = pd.Series(index=attributes)
            s['T'] = T
            s['p'] = p
            s['epsilon'] = epsilon
            s['d'] = d
            s['m_dot'] = m_dot
            s['rho'] = rho
            s['mu'] = mu
            s['A'] = A
            s['U'] = U
            s['Re'] = Re
            s['f'] = f
            df = df.append(s, ignore_index=True)

# plot
sns.set_context('paper')
ax = sns.relplot(x='Re', y='f', hue='p', data=df, col='epsilon', legend='full', palette='colorblind')
plt.savefig('friction_coefficient.png', dpi=300)
plt.close()
