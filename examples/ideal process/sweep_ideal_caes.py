from caes import CAES
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pwr_incs = [100, 500, 1000, 5000]


attributes = ['pwr_inc', 'pmin', 'PR', 'RTE']
df = pd.DataFrame(columns=attributes)
pmins = [1e3]#[0.5e3, 1.0e3, 1.5e3]
PRs = np.arange(1.2, 2.0, 0.1)

for pwr_inc in pwr_incs:
    for pmin in pmins:
        for PR in PRs:
            inputs = CAES.get_default_inputs()
            inputs['p_store_min'] = pmin
            inputs['p_store_init'] = pmin
            inputs['p_store_max'] = pmin * PR
            system = CAES(inputs=inputs)
            system.single_cycle(pwr_inc)
            results = system.analyze_performance()

            s = pd.Series(index=attributes)
            s['pwr_inc'] = pwr_inc
            s['pmin'] = pmin / 1000.0
            s['PR'] = PR
            s['RTE'] = results['RTE']
            df = df.append(s, ignore_index=True)
            print('pwr_inc:' + str(pwr_inc))
            print('pmin:' + str(pmin))
            print('PR:' + str(PR))

sns.scatterplot(x='PR', y='RTE', hue='pmin', style='pwr_inc', data=df)
plt.savefig('demo.png', dpi=600)
