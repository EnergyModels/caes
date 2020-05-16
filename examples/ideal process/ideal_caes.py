from caes import CAES
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pwr = 1000000.0
inputs = CAES.get_default_inputs()
inputs['p_store_min'] = 10.0e3
inputs['p_store_init'] = 10.0e3
inputs['p_store_max'] = 22.0e3
system = CAES(inputs=inputs)
system = CAES()

# system = CAES()
system.single_cycle(pwr)
results = system.analyze_performance()
system.data.to_csv('data.csv')
print(results)