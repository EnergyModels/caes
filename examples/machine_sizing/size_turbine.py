from caes import size_caes_trb
import seaborn as sns
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import pandas as pd

# --------------
# analysis conditions - fixed
# --------------
p_in = 100.0  # [bar]
p_out = 1.01325  # [bar]
t_in = 298.15  # [K]
t_out = 298.15  # [K]
RPM = 3600  # [rpm]

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
t2 = t_in * (p_out / p_in) ** ((n - 1.0) / n)  # [K]
w = 1.0 * R * (t2 - t_in) / (1.0 - n)  # [kJ/kg]

# --------------
# run sweep
# --------------
pwrs = [0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]  # [MW]
pistons = [False]
designs = pd.DataFrame()
m_dot_dict = {}
for piston in pistons:
    for pwr in pwrs:
        # calculate flow rate for selected power rating
        m_dot = pwr * 1E3 / w
        m_dot_dict[m_dot] = pwr
        design = size_caes_trb(p_in=p_in, t_in=t_in - 273.15, t_out=t_out - 273.15, p_out=p_out, m_dot=m_dot,
                               RPM_low=RPM, RPM_high=RPM, RPM_cases=1, piston=piston, debug=False)

        # save power rating
        design['pwr'] = pwr

        # store results
        if len(designs) == 0:
            designs = design
        else:
            designs = designs.append(design, ignore_index=True)

# --------------
# Plot Results
# --------------
sns.scatterplot(x='pwr', y='eff', hue='type', style='Nstg', data=designs)
plt.savefig('trb_sizing.png', dpi=1000)
