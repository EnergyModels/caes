from caes import ICAES, monteCarloInputs
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import time
import os
from datetime import datetime


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

        # primary design choices
        inputs['r_w'] = sweep_input['r_w']  # [m]

        # additional geophysical parameters
        inputs['T_atm'] = sweep_input['T_atm']  # [C]
        inputs['p_atm'] = sweep_input['p_atm']  # [MPa]
        inputs['T_water'] = sweep_input['T_water']  # [C]
        inputs['p_water'] = sweep_input['p_water']  # [MPa]
        inputs['p_hydro_grad'] = sweep_input['p_hydro_grad']  # [MPa/km]
        inputs['p_frac_grad'] = sweep_input['p_frac_grad']  # [MPa/km]
        inputs['T_grad_m'] = sweep_input['T_grad_m']  # [C/km]
        inputs['T_grad_b'] = sweep_input['T_grad_b']  # [C]
        inputs['loss_m_air'] = sweep_input['loss_m_air']  # [-]

        # design choice
        inputs['epsilon'] = sweep_input['epsilon']  # [-]
        inputs['safety_factor'] = sweep_input['safety_factor']  # [-]
        inputs['loss_mech'] = sweep_input['loss_mech']  # [-]
        inputs['loss_gen'] = sweep_input['loss_gen']  # [-]
        inputs['mach_limit'] = sweep_input['mach_limit']  # [-]
        inputs['eta_pump'] = sweep_input['eta_pump']  # [-]
        inputs['ML_cmp1'] = sweep_input['ML_cmp1']  # [-]
        inputs['ML_cmp2'] = sweep_input['ML_cmp2']  # [-]
        inputs['ML_cmp3'] = sweep_input['ML_cmp3']  # [-]
        inputs['ML_exp1'] = sweep_input['ML_exp1']  # [-]
        inputs['ML_exp2'] = sweep_input['ML_exp2']  # [-]
        inputs['ML_exp3'] = sweep_input['ML_exp3']  # [-]

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
    xlsx_filename = 'user_inputs_sizing_monte_carlo.xlsx'  # Excel file with inputs
    sheet_names = ['fixed_diameter', 'geophysical']  # Excel sheet_names
    iterations = 1000  # number of runs per scenario
    ncpus = 6  # number of cpus to use
    capacity = 200  # [MW]
    duration = 24  # [hr]

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    sweep_inputs = pd.DataFrame()
    for sheet_name in sheet_names:
        df_scenario = monteCarloInputs(xlsx_filename, sheet_name, iterations)
        sweep_inputs = sweep_inputs.append(df_scenario)

    # reset index (appending messes up indices)
    sweep_inputs = sweep_inputs.reset_index()

    sweep_inputs.loc[:, 'capacity_MW'] = capacity
    sweep_inputs.loc[:, 'duration_hr'] = duration

    # count number of cases
    n_cases = sweep_inputs.shape[0]

    # save inputs
    sweep_inputs.to_csv('mc_inputs.csv')

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
    df.to_csv('mc_results.csv')

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
