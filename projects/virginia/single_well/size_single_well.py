from caes import ICAES
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
    kW_in = sweep_input['capacity_MW'] * 1e3
    kWh_in = sweep_input['capacity_MW'] * sweep_input['duration_hr'] * 1e3
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
        inputs['depth'] = sweep_input['depth_m']  # porosity depth [m]
        inputs['h'] = sweep_input['thickness_m']  # porosity thickness [m]
        inputs['phi'] = sweep_input['porosity']  # formation porosity [-]
        inputs['k'] = sweep_input['permeability_mD']  # formation permeability [mD]

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
    ncpus = 1  # number of cpus to use
    debug = False

    depth = 1402.35  # [m]
    h = 62.44  # [m]
    phi = 0.2292  # [-]
    k = 38.33  # [mD]
    capacity = 200  # [MW]
    duration = 10  # [hr]

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()

    entries = ['depth_m', 'thickness_m', 'porosity', 'capacity_MW', 'duration_hr', 'permeability_mD']
    s = pd.Series(index=entries)
    s['depth_m'] = depth
    s['thickness_m'] = h
    s['porosity'] = phi
    s['capacity_MW'] = capacity
    s['duration_hr'] = duration
    s['permeability_mD'] = k
    sweep_inputs = sweep_inputs.append(s, ignore_index=True)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    # count number of cases
    n_cases = sweep_inputs.shape[0]

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
    df.to_csv('sizing_results.csv')
