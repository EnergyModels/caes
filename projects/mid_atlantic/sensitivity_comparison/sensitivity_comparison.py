from caes import ICAES2
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime


# =====================
# function to enable parameter sweep
# =====================
def parameter_sweep(sensitivity_input):
    start = time.time()

    # create system
    inputs = ICAES2.get_default_inputs()
    for variable in sensitivity_input.index:
        inputs[variable] = sensitivity_input[variable]
    system = ICAES2(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle()
    results = system.analyze_performance()
    end = time.time()
    results['solve_time'] = end - start

    # combine inputs and results to return in single series
    single_output = pd.concat([sensitivity_input, results])
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
    sheet_names = ['PJM', 'NYISO', 'ISONE',
                   'MK_5', 'MK_10', 'MK_15', 'MK_20',
                   'LK_10', 'LK_15', 'LK_20', 'LK_25', 'LK_30',
                   'UJ_20', 'UJ_25', 'UJ_30']  # Excel sheet_names

    sheet_names = ['MK_3',
                   'LK_1', 'LK_5']  # Excel sheet_names
    ncpus = 3  # number of cpus to use
    float_perm = 0.1  # permutation of float inputs (0.1 = +/-10%)
    int_perm = 1  # permutation of integer inputs ( 1 = +/-1)

    wrkdir = os.getcwd()
    for sheet_name in sheet_names:



        # ------------------
        # create sensitivity_inputs dataframe
        # ------------------
        os.chdir(wrkdir)
        user_input = pd.read_excel(xlsx_filename, sheet_name=sheet_name)

        # create folder to store results
        result_dir = os.path.join(wrkdir, sheet_name)
        try:
            os.stat(result_dir)
        except:
            os.mkdir(result_dir)
        os.chdir(result_dir)

        # indices of variables to perform sensitivity analysis on
        ind = user_input.Include == 'Y'
        # extract variable names, and calculate number of simulations/cases
        variables = user_input.Variable.loc[ind].values
        n_cases = 1 + 2 * len(variables)

        # create dataframe
        inputs = pd.DataFrame(index=range(n_cases), columns=variables)
        inputs.loc[:, 'sensitivity_var'] = 'baseline'
        inputs.loc[:, 'permutation'] = 0.0

        # populate with baseline values
        for variable in variables:
            ind = user_input.Variable == variable
            inputs.loc[:, variable] = float(user_input.loc[ind, 'Baseline'].values)

        # apply permutations
        n = 1
        for variable in variables:
            ind = user_input.Variable == variable

            # store variable name
            inputs.loc[n, 'sensitivity_var'] = variable
            inputs.loc[n + 1, 'sensitivity_var'] = variable
            # ----------
            # float#
            # ----------
            if user_input.loc[ind, 'Type'].values == 'float':
                inputs.loc[n, variable] = inputs.loc[n, variable] * (1.0 + float_perm)
                inputs.loc[n + 1, variable] = inputs.loc[n+1, variable] * (1.0 - float_perm)
                inputs.loc[n, 'permutation'] = (1.0 + float_perm)
                inputs.loc[n + 1, 'permutation'] = (1.0 - float_perm)
            # ----------
            # integer
            # ----------
            if user_input.loc[ind, 'Type'].values == 'integer':
                inputs.loc[n, variable] = inputs.loc[n, variable] + int_perm
                inputs.loc[n + 1, variable] = inputs.loc[n+1, variable] - int_perm
                inputs.loc[n, 'permutation'] = int_perm
                inputs.loc[n + 1, 'permutation'] = - int_perm

            # increase counter
            n = n + 2

        # count number of cases
        n_cases = inputs.shape[0]

        # save inputs
        inputs.to_csv('sensitivity_inputs.csv')

        try:
            ncpus = int(os.getenv('NUM_PROCS'))  # try to use variable defined in sbatch script
        except:
            ncpus = ncpus  # otherwise default to this number of cores

        # run each case using parallelization
        with parallel_backend('multiprocessing', n_jobs=ncpus):
            output = Parallel(n_jobs=ncpus, verbose=5)(
                delayed(parameter_sweep)(inputs.loc[index])
                for index in
                range(n_cases))
        df = pd.DataFrame(output)

        # save results
        df.to_csv('sensitivity_results.csv')

        # save total study time
        end = time.time()
        run_time = (end - start) / 3600.0
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f = open("history_runtime.txt", "a")
        f.write('\n')
        f.write('Last run : ' + dt_string + '\n')
        f.write('Total run time [h]: ' + str(round(run_time, 3)) + '\n')
        f.write('\n')
        f.close()
