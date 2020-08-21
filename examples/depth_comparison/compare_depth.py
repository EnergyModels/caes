from caes import ICAES
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ===========================
# common inputs
# ===========================
h = 62.44  # thickness [m]
phi = 0.2292  # porosity
k = 38.33  # permeability [mD]
m_dot = 200.0  # mass flow rate [kg/s]
r_f = 100.0  # formation radius [m]
r_w = 0.41 / 2.0  # well radius [m]

depths = [1000.0, 2000.0, 3000.0, 4000.0, 5000.0]  # depth [m]
all_results = pd.DataFrame()

# iterate through depths
for depth in depths:

    # iterate through test cases
    for i in range(5):

        inputs = ICAES.get_default_inputs()
        inputs['depth'] = depth
        inputs['h'] = h
        inputs['phi'] = phi
        inputs['k'] = k
        inputs['r_f'] = r_f
        inputs['r_w'] = r_w
        inputs['m_dot'] = m_dot

        # ===========================
        # cases
        # ===========================
        if i == 0:
            casename = 'default'

        elif i == 1:  # i == 1
            casename = 'zero_delta_T'
            inputs['T_grad_m'] = 0.0

        elif i == 2:  # i == 2
            casename = 'zero_mass_leakage'
            inputs['loss_m_air'] = 0.0

        elif i == 3:  # i == 3
            casename = 'inc_ML'

            ML = 1.1
            inputs['ML_cmp1'] = ML
            inputs['ML_cmp2'] = ML
            inputs['ML_cmp3'] = ML

            inputs['ML_exp1'] = ML
            inputs['ML_exp2'] = ML
            inputs['ML_exp3'] = ML

        else:  # i == 4
            casename = 'dec_ML'

            ML = 0.9
            inputs['ML_cmp1'] = ML
            inputs['ML_cmp2'] = ML
            inputs['ML_cmp3'] = ML

            inputs['ML_exp1'] = ML
            inputs['ML_exp2'] = ML
            inputs['ML_exp3'] = ML

        # ===========================
        # create system and run
        # ===========================
        system = ICAES(inputs=inputs)
        system.single_cycle()
        results = system.analyze_performance()

        # ===========================
        # append results
        # ===========================
        comb = pd.concat([inputs, results])
        comb['casename'] = casename
        all_results = all_results.append(comb, ignore_index=True)

all_results.to_csv('results.csv')

sns.scatterplot(x='depth', y='RTE', hue='casename', data=all_results)
plt.savefig('depth_comparison.png')
