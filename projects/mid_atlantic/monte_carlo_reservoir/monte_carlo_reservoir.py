from caes import ICAES, monteCarloInputs
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime


# =====================
# function to enable sizing for each entry in input file (XLSX_filename)
# =====================
def parameter_sweep(sweep_input, MW_in=100.0, MWh_in=1000.0, debug=True):
    start = time.time()

    # convert inputs to model units
    kW_in = MW_in * 1e3
    kWh_in = MWh_in * 1e3
    if debug:
        print('\nStarting sizing')
        print("kW_in (desired)  : " + str(round(kW_in, 3)))
        print("kWh_in (desired) : " + str(round(kWh_in, 3)))
        print("\nDepth (m)        : " + str(sweep_input['depth_m']))
        print("Thickness (m)    : " + str(sweep_input['thickness_m']))
        print("Porosity (-)     : " + str(sweep_input['porosity']))
        print("Permeability (mD): " + str(sweep_input['permeability_mD']))

    # allowable calculation error
    error = 1e-6

    # maximum number of iterations
    count_max = 200

    # initial guesses
    m_dot = 10.0
    r_f = 10.0

    # initial results
    kW_in_actual = 0.0
    kWh_in_actual = 0.0

    count = 0
    while abs(kW_in_actual - kW_in) / kW_in + abs(kWh_in_actual - kWh_in) / kWh_in > error:
        if debug:
            print("\nIteration : " + str(count))
            print("m_dot       : " + str(round(m_dot, 3)))
            print("r_f         : " + str(round(r_f, 3)))

        # create system
        inputs = ICAES.get_default_inputs()
        # user inputs
        inputs['depth'] = sweep_input['depth']  # porosity depth [m]
        inputs['h'] = sweep_input['h']  # porosity thickness [m]
        inputs['phi'] = sweep_input['phi']  # formation porosity [-]
        inputs['k'] = sweep_input['k']  # formation permeability [mD]

        # current guess/iteration
        inputs['m_dot'] = m_dot  # [kg/s]
        inputs['r_f'] = r_f  # [m]
        system = ICAES(inputs=inputs)

        # run single cycle and analyze
        system.single_cycle()
        results = system.analyze_performance()

        # extract results of interest
        kW_in_actual = results['kW_in_avg']
        kWh_in_actual = results['kWh_in']

        # update guesses
        tau = 0.5  # solver time constant
        m_dot = m_dot * (1.0 + tau * (kW_in - kW_in_actual) / kW_in)  # m_dot linearly linked to kW
        r_f = r_f * (1.0 + tau ** 2 * (kWh_in - kWh_in_actual) / kWh_in_actual)  # r_f exponentially linked to kWh

        count = count + 1
        if count > count_max:
            break

        if debug:
            print("MW_in_avg   : " + str(round(kW_in_actual / 1e3, 3)))
            print("MWh_in      : " + str(round(kWh_in_actual / 1e3, 3)))

    end = time.time()
    results['solve_time'] = end - start
    results['iterations'] = count
    results['m_dot'] = m_dot
    results['r_f'] = r_f

    # combine inputs and results to return in single series
    single_output = pd.concat([sweep_input, results])
    return single_output


# =====================
# main program
# =====================
start = time.time()
if __name__ == '__main__':
    # ==============
    # user inputs
    # ==============
    xlsx_filename = 'user_inputs.xlsx'  # Excel file with inputs
    sheet_names = ['monte_carlo']  # Excel sheet_names
    iterations = 10000  # number of runs per scenario
    ncpus = int(os.getenv('NUM_PROCS'))  # number of cpus to use
    pwr_rating = 100  # [MW]
    energy_rating = 10 * pwr_rating  # [MWh]
    debug = False

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
            delayed(parameter_sweep)(sweep_inputs.loc[index], MW_in=pwr_rating, MWh_in=energy_rating, debug=debug)
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