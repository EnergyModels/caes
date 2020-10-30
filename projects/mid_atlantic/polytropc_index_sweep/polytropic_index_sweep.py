from caes import ICAES2
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
# main program
# =====================
if __name__ == '__main__':
    start = time.time()
    # ==============
    # user inputs
    # ==============
    ncpus = 6  # number of cpus to use
    debug = False

    # location-based parameters
    sites = ['PJM', 'NYISO', 'ISONE']
    depths = [1402.35, 1123.16, 1157.07]  # [m]
    hs = [62.44, 297.50, 199.14]  # [m]
    phis = [0.2292, 0.2820, 0.2651]  # [-]
    ks = [38.33, 2.373174, 2.121646]  # [mD]

    # constants
    capacity = 200
    duration = 24

    # sweep parameters (nparray)
    polytropic_indices = np.arange(1.01, 1.41, 0.01)

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()

    entries = ['depth_m', 'thickness_m', 'porosity', 'capacity_MW', 'duration_hr', 'permeability_mD', 'k_type']
    for site, depth, h, phi, k in zip(sites, depths, hs, phis, ks):
        for polytropic_index in polytropic_indices:
            s = pd.Series(index=entries)
            s['site'] = site
            s['depth_m'] = depth
            s['thickness_m'] = h
            s['porosity'] = phi
            s['capacity_MW'] = capacity
            s['duration_hr'] = duration
            s['permeability_mD'] = k
            s['n_cmp1'] = polytropic_index
            s['n_exp1'] = polytropic_index
            sweep_inputs = sweep_inputs.append(s, ignore_index=True)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    # count number of cases
    n_cases = sweep_inputs.shape[0]

    # save inputs
    sweep_inputs.to_csv('sizing_study_inputs.csv')

    try:
        ncpus = int(os.getenv('NUM_PROCS'))  # try to use variable defined in sbatch script
    except:
        ncpus = ncpus  # otherwise default to this number of cores

    # run each case using parallelization
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(parameter_sweep)(sweep_inputs.loc[index], debug=debug)
            for index in
            range(n_cases))
    df = pd.DataFrame(output)

    # save results
    df.to_csv('sizing_study_results.csv')

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
