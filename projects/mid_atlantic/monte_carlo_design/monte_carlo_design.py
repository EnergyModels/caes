from caes import ICAES, monteCarloInputs
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime


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
    xlsx_filename = 'user_inputs.xlsx'  # Excel file with inputs
    sheet_names = ['monte_carlo']  # Excel sheet_names
    iterations = 10000  # number of runs per scenario
    ncpus = int(os.getenv('NUM_PROCS'))  # number of cpus to use

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()
    for sheet_name in sheet_names:
        df_scenario = monteCarloInputs(xlsx_filename, sheet_name, iterations)
        sweep_inputs = sweep_inputs.append(df_scenario)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    # count number of cases
    n_cases = sweep_inputs.shape[0]

    # save inputs
    sweep_inputs.to_csv('mc_inputs.csv')

    # run each case using parallelization
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(parameter_sweep)(sweep_inputs.loc[index])
            for index in
            range(n_cases))
    df = pd.DataFrame(output)

    # save results
    df.to_csv('mc_results.csv')

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
