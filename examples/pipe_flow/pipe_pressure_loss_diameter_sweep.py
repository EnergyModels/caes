from caes import pipe_fric_dp, pipe_grav_dp
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

# fixed inputs
T = 290  # [K]
epsilon = 0.002 * 1.0e-3  # roughness [m]
depth = 1420  # depth [m]
p = 15.0 # pressures [MPa]

# parameters to sweep
m_dots = np.arange(100, 501, 100)  # flow rates [kg/s]
diameters = np.arange(0.1, 0.51, 0.1) # diameter [m]

# dataframe to store results
attributes = ['T', 'p', 'epsilon', 'depth', 'd', 'm_dot', 'rho', 'mu',  # inputs
              'dp_grav', 'dp_fric', 'f']  # results
df = pd.DataFrame(columns=attributes)

# perform parameter sweep
for m_dot in m_dots:
    for d in diameters:
        # fluid properties, inputs are degrees K and Pa
        rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, "Air.mix")  # density [kg/m3]
        mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, "Air.mix")  # viscosity [Pa*s]

        # pressure drop
        dp_grav = pipe_grav_dp(m_dot=m_dot, rho=rho, z=depth)
        dp_fric, f = pipe_fric_dp(epsilon=epsilon, d=d, depth=depth, m_dot=m_dot, rho=rho, mu=mu)

        # save results
        s = pd.Series(index=attributes)
        s['T'] = T
        s['p'] = p
        s['epsilon'] = epsilon
        s['depth'] = depth
        s['d'] = d
        s['m_dot'] = m_dot
        s['rho'] = rho
        s['mu'] = mu
        s['dp_grav'] = dp_grav
        s['dp_fric'] = dp_fric
        s['f'] = f
        df = df.append(s, ignore_index=True)

# plot
sns.set_context('paper')
ax = sns.relplot(x='m_dot', y='dp_grav', hue='d', data=df, legend='full', palette='colorblind')
plt.savefig('pipe_gravity_losses_diameter.png', dpi=300)
plt.close()

# plot
sns.set_context('paper')
ax = sns.relplot(x='d', y='dp_fric', hue='m_dot', data=df, legend='full', palette='colorblind')
plt.ylim([0,15])
plt.savefig('pipe_friction_losses_diameter.png', dpi=300)

plt.close()
