from caes import ICAES2
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime


# =====================
# function to enable sensitivity analysis
# =====================
def sizing_and_sensitivity(wrkdir, xlsx_filename, sheet_name, capacity, duration, polytropic_index, float_perm,
                           int_perm, debug):
    # create folder to store results
    result_dir = os.path.join(wrkdir, sheet_name)
    try:
        os.stat(result_dir)
    except:
        os.mkdir(result_dir)

    # -----------------------------
    # prepare for sizing
    # -----------------------------
    entries = ['depth_m', 'thickness_m', 'porosity', 'capacity_MW', 'duration_hr', 'permeability_mD', 'n_cmp1',
               'n_exp1']
    user_input = pd.read_excel(xlsx_filename, sheet_name=sheet_name)
    user_input = user_input.set_index('Variable')
    s = pd.Series(index=entries)
    s['sheet_name'] = sheet_name
    s['depth_m'] = user_input.loc['depth', 'Baseline']
    s['thickness_m'] = user_input.loc['h', 'Baseline']
    s['porosity'] = user_input.loc['phi', 'Baseline']
    s['capacity_MW'] = capacity
    s['duration_hr'] = duration
    s['permeability_mD'] = user_input.loc['k', 'Baseline']
    s['r_w'] = user_input.loc['r_w', 'Baseline']
    s['n_cmp1'] = polytropic_index
    s['n_exp1'] = polytropic_index

    # ------------------
    # run sizing
    # ------------------
    sized_result = sizing(s, debug=False)

    # save inputs
    os.chdir(result_dir)
    sized_result.to_csv('sizing_results.csv')

    # ------------------
    # prepare for sensitivity
    # ------------------
    os.chdir(wrkdir)
    user_input = pd.read_excel(xlsx_filename, sheet_name=sheet_name)
    os.chdir(result_dir)

    # use results from sizing
    m_dot = pd.Series()
    m_dot['Variable'] = 'm_dot'
    m_dot['Baseline'] = sized_result['m_dot']
    m_dot['Include'] = 'Y'
    m_dot['Type'] = 'float'
    m_dot['Note'] = 'from sizing'
    user_input = user_input.append(m_dot, ignore_index=True)

    r_f = pd.Series()
    r_f['Variable'] = 'r_f'
    r_f['Baseline'] = sized_result['r_f']
    r_f['Include'] = 'Y'
    r_f['Type'] = 'float'
    r_f['Note'] = 'from sizing'
    user_input = user_input.append(r_f, ignore_index=True)

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
            inputs.loc[n + 1, variable] = inputs.loc[n + 1, variable] * (1.0 - float_perm)
            inputs.loc[n, 'permutation'] = (1.0 + float_perm)
            inputs.loc[n + 1, 'permutation'] = (1.0 - float_perm)
        # ----------
        # integer
        # ----------
        if user_input.loc[ind, 'Type'].values == 'integer':
            inputs.loc[n, variable] = inputs.loc[n, variable] + int_perm
            inputs.loc[n + 1, variable] = inputs.loc[n + 1, variable] - int_perm
            inputs.loc[n, 'permutation'] = int_perm
            inputs.loc[n + 1, 'permutation'] = - int_perm

        # increase counter
        n = n + 2

    # save inputs
    inputs.to_csv('sensitivity_inputs.csv')

    # count number of cases
    n_cases = inputs.shape[0]

    # ------------------
    # run sensitivity
    # ------------------
    df = pd.DataFrame()
    for index in range(n_cases):
        output = sensitivity(inputs.loc[index])
        df = df.append(output, ignore_index=True)

    # ------------------
    # run sensitivity
    # ------------------
    df.to_csv('sensitivity_results.csv')


# =====================
# function to enable sizing for a single site
# =====================
def sizing(sweep_input, debug=True):
    start = time.time()

    # convert inputs to model units
    kW_out = sweep_input['capacity_MW'] * 1e3
    kWh_out = sweep_input['capacity_MW'] * sweep_input['duration_hr'] * 1e3
    if debug:
        print('\nStarting sizing')
        print("kW_out (desired) : " + str(round(kW_out, 3)))
        print("kWh_out (desired): " + str(round(kWh_out, 3)))
        print("\nDepth (m)      : " + str(sweep_input['depth_m']))
        print("Thickness (m)    : " + str(sweep_input['thickness_m']))
        print("Porosity (-)     : " + str(sweep_input['porosity']))
        print("Permeability (mD): " + str(sweep_input['permeability_mD']))
        print("Well radius (m)  : " + str(sweep_input['r_w']))

    # allowable calculation error
    error = 1e-6

    # maximum number of iterations
    count_max = 200

    # initial guesses
    m_dot = 10.0
    r_f = 10.0

    # initial results
    kW_out_actual = 0.0
    kWh_out_actual = 0.0

    count = 0
    while abs(kW_out_actual - kW_out) / kW_out + abs(kWh_out_actual - kWh_out) / kWh_out > error:
        if debug:
            print("\nIteration : " + str(count))
            print("m_dot       : " + str(round(m_dot, 3)))
            print("r_f         : " + str(round(r_f, 3)))

        # create system
        inputs = ICAES2.get_default_inputs()
        # user inputs
        inputs['depth'] = sweep_input['depth_m']  # porosity depth [m]
        inputs['h'] = sweep_input['thickness_m']  # porosity thickness [m]
        inputs['phi'] = sweep_input['porosity']  # formation porosity [-]
        inputs['k'] = sweep_input['permeability_mD']  # formation permeability [mD]
        inputs['r_w'] = sweep_input['r_w']  # well radius [m]

        # machinery polytropic index
        inputs['n_cmp1'] = sweep_input['n_cmp1']
        inputs['n_exp1'] = sweep_input['n_exp1']

        # current guess/iteration
        inputs['m_dot'] = m_dot  # [kg/s]
        inputs['r_f'] = r_f  # [m]
        system = ICAES2(inputs=inputs)

        # run single cycle and analyze
        system.single_cycle()
        results = system.analyze_performance()

        # extract results of interest
        kW_out_actual = results['kW_out_avg']
        kWh_out_actual = results['kWh_out']

        # update guesses
        tau = 0.5  # solver time constant
        m_dot = m_dot * (1.0 + tau * (kW_out - kW_out_actual) / kW_out)  # m_dot linearly linked to kW
        r_f = r_f * (1.0 + tau ** 2 * (kWh_out - kWh_out_actual) / kWh_out_actual)  # r_f exponentially linked to kWh

        count = count + 1
        if count > count_max:  # sizing unsuccessful
            results['errors'] = True
            break

        if debug:
            print("MW_out_avg   : " + str(round(kW_out_actual / 1e3, 3)))
            print("MWh_out      : " + str(round(kWh_out_actual / 1e3, 3)))

    end = time.time()
    results['solve_time'] = end - start
    results['iterations'] = count
    results['m_dot'] = m_dot
    results['r_f'] = r_f

    # print out RTE
    print(results['RTE'])

    # combine inputs and results to return in single series
    single_output = pd.concat([sweep_input, results])
    return single_output


# =====================
# function to perform a single sensitivity permutation
# =====================
def sensitivity(sensitivity_input):
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
    # ---------------------
    # user inputs
    # ---------------------
    xlsx_filename = 'user_inputs.xlsx'  # Excel file with inputs
    sheet_names = ['PJM', 'NYISO', 'ISONE']  # Excel sheet_names
    ncpus = 1  # default number of cpus to use

    # sizing
    capacity = 200  # [MW]
    duration = 24  # [hr]
    polytropic_index = 1.1  # [-]

    # sensitivity inputs
    float_perm = 0.1  # permutation of float inputs (0.1 = +/-10%)
    int_perm = 1  # permutation of integer inputs ( 1 = +/-1)

    # debug?
    debug = False

    # ---------------------
    # check if more CPUs are available
    # ---------------------
    try:
        ncpus = int(os.getenv('NUM_PROCS'))  # try to use variable defined in sbatch script
    except:
        ncpus = ncpus  # otherwise default to this number of cores

    wrkdir = os.getcwd()

    # ---------------------
    # run each case using parallelization
    # ---------------------
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(sizing_and_sensitivity)(wrkdir, xlsx_filename, sheet_name, capacity, duration, polytropic_index,
                                            float_perm, int_perm, debug) for sheet_name in sheet_names)

    # ---------------------
    # save total study time
    # ---------------------
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
