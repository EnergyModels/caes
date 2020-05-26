from caes import size_caes_cmp
import seaborn as sns
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import pandas as pd
import numpy as np

# --------------
# analysis conditions - fixed
# --------------
p_in = 1.01325  # [bar]
p_out = 100.0  # [bar]
t_in = 298.15  # [K]

# --------------
# specific work
# --------------
# air properties
fluid = 'Air.mix'
CP = PropsSI('CPMASS', "T", t_in, "P", p_in, fluid)  # J/Kg-K
CV = PropsSI('CVMASS', "T", t_in, "P", p_in, fluid)  # J/Kg-K
k = CP / CV
MW = PropsSI('M', fluid) * 1000.0  # kg/kmol
R_bar = PropsSI('GAS_CONSTANT', fluid)  # kJ/kmol/K
R = R_bar / MW  # kJ/kg-K
# polytropic work
n = k  # polytropic exponent
t_out = t_in * (p_out / p_in) ** ((n - 1.0) / n)  # [K]
w = -1.0 * R * (t_out - t_in) / (1.0 - n)  # [kJ/kg]

# --------------
# run sweep @ 3600 rpm
# --------------
RPM_low = 900
RPM_high = 10000
RPM_cases = 11
RPMs = np.arange(900,10000,900)
pwrs = [0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, 100.0, 250.0, 500.0, 750.0, 1000.0]  # [MW]
types = ['piston', 'radial-mixed-axial']
designs = pd.DataFrame()
m_dot_dict = {}
for machine_type in types:
    for pwr in pwrs:
        for RPM in RPMs:
            # calculate flow rate for selected power rating
            m_dot = pwr * 1E3 / w
            m_dot_dict[m_dot] = pwr
            design = size_caes_cmp(p_in=p_in, t_in=t_in - 273.15, p_out=p_out, m_dot=m_dot,
                                   RPM_low=RPM, RPM_high=RPM, RPM_cases=1,
                                   machine_type=machine_type, debug=False)

            # save power rating
            design['pwr'] = pwr

            # store results
            if len(designs) == 0:
                designs = design
            else:
                designs = designs.append(design, ignore_index=True)

# --------------
# plot results
# --------------
ax = sns.scatterplot(x='pwr', y='eff', hue='type', data=designs)
ax.set(xscale='log')
ax.set_xlabel('Power [MW]')
ax.set_ylabel('Isentropic efficiency [fr]')
plt.savefig('cmp_sizing.png', dpi=300)
plt.close()

# --------------
# costs
# --------------
designs2 = designs[designs['type'] != 'Rotary Piston']

machine_types = ['Piston', 'Radial', 'Mixed', 'Axial']
costs = [900, 500, 500, 500]

for machine_type, cost in zip(machine_types, costs):
    designs2.loc[designs2.loc[:, 'type'] == machine_type, 'Cost ($/kW)'] = cost

# calculate cost per kW in
designs2.loc[:, 'Cost ($/kWin)'] = designs2.loc[:, 'Cost ($/kW)'] / designs2.loc[:, 'eff']

# --------------
# plot results - costs
# --------------
ax = sns.scatterplot(x='pwr', y='Cost ($/kWin)', hue='type', data=designs2)
ax.set(xscale='log')
ax.set_xlabel('Power [MW]')
plt.savefig('cmp_sizing_cost.png', dpi=300)
plt.close()
