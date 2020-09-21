from caes import ICAES, monteCarloInputs
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime
import numpy as np

# =====================
# function to enable sizing for each entry in input file (XLSX_filename)
# =====================
def parameter_sweep(sweep_input, debug=True):
    start = time.time()

    # convert inputs to model units
    kW_out = sweep_input['capacity_MW'] * 1e3
    kWh_out = sweep_input['capacity_MW'] * sweep_input['duration_hr'] * 1e3
    if debug:
        print('\nStarting sizing')
        print("kW_out (desired)  : " + str(round(kW_out, 3)))
        print("kWh_out (desired) : " + str(round(kWh_out, 3)))

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
        inputs = ICAES.get_default_inputs()
        # user inputs
        # primary geophysical parameters
        inputs['depth'] = sweep_input['depth']  # [m]
        inputs['h'] = sweep_input['h']  # [m]
        inputs['phi'] = sweep_input['phi']  # [-]
        inputs['k'] = sweep_input['k']  # [mD]

        # Update machinery performance
        if inputs['depth'] > 1500:
            # compression - mass load per stage (ratio of water to air by mass)
            inputs['ML_cmp1'] = 2.0
            inputs['ML_cmp2'] = 1.5
            inputs['ML_cmp3'] = 1.0
            inputs['ML_cmp4'] = 0.5  # <0 - unused
            inputs['ML_cmp5'] = -1  # <0 - unused

            # expansion - mass loading per stage
            inputs['ML_exp1'] = 0.5
            inputs['ML_exp2'] = 1.0
            inputs['ML_exp3'] = 1.5
            inputs['ML_exp4'] = 2.0  # <0 - unused
            inputs['ML_exp5'] = -1  # <0 - unused

            # compression - pressure drop inbetween stages (fraction)
            inputs['delta_p_cmp12'] = 0.0  # between stages 1 and 2
            inputs['delta_p_cmp23'] = 0.02
            inputs['delta_p_cmp34'] = 0.02  # <0 - unused
            inputs['delta_p_cmp45'] = -1  # <0 - unused

            # compression - pressure drop inbetween stages (fraction)
            inputs['delta_p_exp12'] = 0.02  # between stages 1 and 2
            inputs['delta_p_exp23'] = 0.02
            inputs['delta_p_exp34'] = 0.0  # <0 - unused
            inputs['delta_p_exp45'] = -1  # <0 - unused

        # current guess/iteration
        inputs['m_dot'] = m_dot  # [kg/s]
        inputs['r_f'] = r_f  # [m]
        system = ICAES(inputs=inputs)

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
# main program
# =====================
if __name__ == '__main__':
    start = time.time()
    # ==============
    # user inputs
    # ==============
    ncpus = 3  # number of cpus to use

    # constant parameters
    duration = 24  # [hr]
    h = 506.4534957 * 0.3048 # [m], average for LK1
    phi = 0.255528 # [-], average for LK1

    # varied parameters
    # depths = np.arange(1000.0, 5601.0, 100.0)  # [m]
    depths = np.arange(1000.0, 5601.0, 500.0)  # [m]
    # ks = np.array([1.0, 10.0, 100.0, 1000.0, ]) # [mD]
    ks = np.array([10.0, ])  # [mD]
    capacities = np.array([200.0])  # [MW]

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()
    for depth in depths:
        for k in ks:
            for capacity in capacities:
                s = pd.Series(index=['depth', 'k', 'capacity'], dtype='float64')
                s['depth'] = depth
                s['k'] = k
                s['capacity_MW'] = capacity
                sweep_inputs = sweep_inputs.append(s, ignore_index=True)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    sweep_inputs.loc[:, 'h'] = h
    sweep_inputs.loc[:, 'phi'] = phi
    sweep_inputs.loc[:, 'duration_hr'] = duration

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
            delayed(parameter_sweep)(sweep_inputs.loc[index], debug=False)
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
    f = open("history_runtime.txt", "a")
    f.write('\n')
    f.write('Last run : ' + dt_string + '\n')
    f.write('Total run time [h]: ' + str(round(run_time, 3)) + '\n')
    f.write('\n')
    f.close()
