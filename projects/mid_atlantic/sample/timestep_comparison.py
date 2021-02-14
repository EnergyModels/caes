from caes import ICAES2
from math import pi
import pandas as pd

# well parameters
depth = 1123.16  # [m]
h = 297.50  # [m]
phi = 0.2820  # [-]
k = 236.1424  # [mD]
capacity = 200  # [MW]
duration = 24  # [hr]
r_w = 0.41 / 2.0  # [m]
m_dot = 619.6078491  # mass flow rate [kg/s]
r_f = 82.64452305  # formation radius [m]

timesteps_to_try = [1,2,5,10, 50, 75, 100, 125, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

df = pd.DataFrame()

for timesteps in timesteps_to_try:
    # create system
    inputs = ICAES2.get_default_inputs()
    inputs['depth'] = depth
    inputs['h'] = h
    inputs['phi'] = phi
    inputs['k'] = k
    inputs['r_f'] = r_f
    inputs['r_w'] = r_w
    inputs['m_dot'] = m_dot
    inputs['steps'] = timesteps

    system = ICAES2(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle()
    results = system.analyze_performance()
    RTE = results['RTE']

    s = pd.Series()
    s['timesteps'] = timesteps
    s['RTE'] = results['RTE']
    s['kWh_in'] = results['kWh_in']
    s['kWh_out'] = results['kWh_out']
    s['kW_in_avg'] = results['kW_in_avg']
    s['kW_out_avg'] = results['kW_out_avg']
    s['errors'] = results['errors']
    df = df.append(s, ignore_index=True)

df.to_csv('timesteps_comparison.csv')
