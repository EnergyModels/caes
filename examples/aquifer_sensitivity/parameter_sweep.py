from caes import ICAES
import pandas as pd
import numpy as np
from joblib import Parallel, delayed, parallel_backend
import time
from math import exp


# =====================
# function to enable parameter sweep
# =====================
def parameter_sweep(sweep_input):
    start = time.time()

    # create system
    inputs = ICAES.get_default_inputs()
    inputs['depth'] = sweep_input['depth']  # [m]
    inputs['r_f'] = sweep_input['r_f']  # [m]
    inputs['h'] = sweep_input['h']  # [m]
    inputs['phi'] = sweep_input['phi']  # [-]
    inputs['k'] = sweep_input['k']  # [mD]

    system = ICAES(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle(m_dot=sweep_input['m_dot'])
    results = system.analyze_performance()
    end = time.time()
    results['solve_time'] = end - start

    # combine inputs and results to return in single series
    single_output = pd.concat([sweep_input, results])
    return single_output


# =====================
# main program
# =====================
if __name__ == '__main__':
    # ==============
    # user inputs
    # ==============

    # ------------------
    # integer inputs
    # ------------------
    ncpus = 6  # int(os.getenv('NUM_PROCS'))
    # ------------------
    # numpy array inputs
    # ------------------
    # investigated
    depths = np.array([1400])  # p.arange(1000.0, 3000.1, 1000.0)  # aquifer depth [m3] TODO
    r_fs = np.arange(100.0, 500.1, 133.33)  # formation radius [m]
    hs = np.array([50.0, 100.0, 500.0, 1000.0])  # np.arange(50, 1200.1, 380.0)  # formation thickness [m]
    phis = np.arange(0.22, 0.3714, 0.04)  # porosity [-] TODO
    # k, permeability [mD] - calculate later
    m_dots = np.arange(100.0, 400.1, 100.0)  # [kg/s] # calculate later

    # ==============
    # run simulations
    # ==============

    # prepare dataframe to store inpu
    # ts
    attributes = ['depth', 'r_f', 'h', 'phi', 'k', 'm_dot']
    sweep_inputs = pd.DataFrame(columns=attributes)

    count = 0
    for depth in depths:
        for r_f in r_fs:
            for h in hs:
                for phi in phis:
                    for m_dot in m_dots:
                        sweep_inputs.loc[count, 'depth'] = depth
                        sweep_inputs.loc[count, 'r_f'] = r_f
                        sweep_inputs.loc[count, 'h'] = h
                        sweep_inputs.loc[count, 'phi'] = phi
                        sweep_inputs.loc[count, 'k'] = 0.028 * exp(31.16 * phi)  # Fukai et al. 2020
                        sweep_inputs.loc[count, 'm_dot'] = m_dot
                        count = count + 1
    n_cases = sweep_inputs.shape[0]

    # save inputs
    sweep_inputs.to_csv('parameter_sweep_inputs.csv')

    # run each case using parallelization
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(parameter_sweep)(sweep_inputs.loc[index])
            for index in
            range(n_cases))
    df = pd.DataFrame(output)

    # save results
    df.to_csv('parameter_sweep_results.csv')
