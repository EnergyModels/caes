from caes import ICAES, monteCarloInputs
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os


# =====================
# function to enable parameter sweep
# =====================
def parameter_sweep(sweep_input, kW_in, kWh_in):
    start = time.time()

    # allowable calculation error
    error = 1e-6

    # maximum number of iterations
    count_max = 100

    # initial guesses
    m_dot = 10.0
    r_f = 10.0

    # initial results
    kW_in_actual = 0.0
    kWh_in_actual = 0.0

    count = 0
    while abs(kW_in_actual - kW_in) + abs(kWh_in_actual - kWh_in) > error:
        # create system
        inputs = ICAES.get_default_inputs()
        inputs['depth'] = sweep_input['depth']  # [m]
        inputs['h'] = sweep_input['h']  # [m]
        inputs['phi'] = sweep_input['phi']  # [-]
        inputs['k'] = sweep_input['k']  # [mD]

        inputs['m_dot'] = m_dot  # [kg/s]
        inputs['r_f'] = 'r_f'  # [m]
        system = ICAES(inputs=inputs)

        # run single cycle and analyze
        system.single_cycle()
        results = system.analyze_performance()

        # extract results of interest
        kW_in_actual = results['kW_in_avg']
        kWh_in_actual = results['kWh_in']

        # update guesses
        m_dot = m_dot * 0.5 * kW_in / kW_in_actual  # m_dot losses are exponential, 0.5 is to avoid errors
        r_f = r_f * kWh_in / kWh_in_actual

        count = count + 1
        if count > count_max:
            break

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
    xlsx_filename = 'user_inputs.xlsx'  # Excel file with inputs
    sheet_names = ['LK1', 'MK', 'UJ1']  # Excel sheet_names
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
