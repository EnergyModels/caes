from caes import ICAES
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime
import numpy as np


# =====================
# function to enable parameter sweep
# =====================
def parameter_sweep(sweep_input):
    start = time.time()

    # create system
    inputs = ICAES.get_default_inputs()
    inputs['depth'] = sweep_input['depth']  # [m]
    inputs['h'] = sweep_input['h']  # [m]
    inputs['phi'] = sweep_input['phi']  # [-]
    inputs['k'] = sweep_input['k']  # [mD]
    inputs['m_dot'] = sweep_input['m_dot']  # [kg/s]
    inputs['r_f'] = sweep_input['r_f']  # [m]
    inputs['r_w'] = sweep_input['r_w']  # [m]
    system = ICAES(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle()
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
    start = time.time()
    # ==============
    # user inputs
    # ==============
    ncpus = 6  # number of cpus to use

    # constants
    depth = 1402.35  # [m]
    h = 62.44  # [m]
    phi = 0.2292  # [-]

    # scenario inputs (length must match)
    scenario_names = ['low_k', 'med_low_k', 'med_high_k', 'high_k', 'iowa_k']
    k = [0.47, 38.33, 339.0, 2514.41, 3.0]  # [mD]

    # sweep parameters (nparray)
    m_dot = np.arange(50, 501, 50)  # [kg/s]
    r_f = np.arange(20, 201, 20)  # [m]
    r_w = np.arange(0.05, 0.51, 0.05)  # [m]

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()

    entries = ['scenario_name', 'depth', 'h', 'phi', 'k', 'm_dot', 'r_f', 'r_w']
    for scenario_name, k_i in zip(scenario_names, k):
        for m_dot_i in m_dot:
            for r_f_i in r_f:
                for r_w_i in r_w:
                    s = pd.Series(index=entries)
                    s['scenario_name'] = scenario_name
                    s['depth'] = depth
                    s['h'] = h
                    s['phi'] = phi
                    s['k'] = k_i
                    s['m_dot'] = m_dot_i
                    s['r_f'] = r_f_i
                    s['r_w'] = r_w_i
                    sweep_inputs = sweep_inputs.append(s,ignore_index=True)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    # count number of cases
    n_cases = sweep_inputs.shape[0]

    # save inputs
    sweep_inputs.to_csv('sweep_inputs.csv')

    try:
        ncpus = int(os.getenv('NUM_PROCS'))  # try to use variable defined in sbatch script
    except:
        ncpus = ncpus  # otherwise default to this number of cores

    # run each case using parallelization
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(parameter_sweep)(sweep_inputs.loc[index])
            for index in
            range(n_cases))
    df = pd.DataFrame(output)

    # save results
    df.to_csv('sweep_results.csv')

    # save total study time
    end = time.time()
    run_time = (end - start) / 3600.0
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("run_time_history.txt", "a")
    f.write('\n')
    f.write('Last run : ' + dt_string + '\n')
    f.write('Total run time [h]: ' + str(round(run_time, 3)) + '\n')
    f.write('\n')
    f.close()
