from caes import ICAES
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pwr = 1000000.0
system = ICAES()
system.single_cycle(pwr)
# system.debug(pwr)
print('complete')
results = system.analyze_performance()
system.data.to_csv('data.csv')
print(results)

# attributes = ['PR', 'nozzle3', 'RTE']
# df = pd.DataFrame(columns=attributes)
# nozzle3s = [1, 5, 10, 15, 20, 25]
# PRs = np.arange(1.5, 3.0, 0.1)
#
# for PR in PRs:
#     for nozzle3 in nozzle3s:
#         inputs = ICAES.get_default_inputs()
#         inputs['nozzles2'] = nozzle3
#         inputs['p_store_max'] = inputs['p_store_min'] * PR
#         system = ICAES(inputs=inputs)
#         # system.p_store_max = system.p_store_min * PR
#         # system.nozzles3 = nozzle3
#         system.single_cycle(pwr)
#         results = system.analyze_performance()
#         print(results)
#
#         s = pd.Series(index=attributes)
#         s['PR'] = PR
#         s['nozzle3'] = nozzle3
#         s['RTE'] = results['RTE']
#         df = df.append(s, ignore_index=True)
#
# sns.lineplot(x='PR', y='RTE', hue='nozzle3', data=df)
# plt.savefig('demo.png', dpi=600)
