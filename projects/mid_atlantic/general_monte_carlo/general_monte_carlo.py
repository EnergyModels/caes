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
    # primary geophysical parameters
    inputs['depth'] = sweep_input['depth']  # [m]
    inputs['h'] = sweep_input['h']  # [m]
    inputs['phi'] = sweep_input['phi']  # [-]
    inputs['k'] = sweep_input['k']  # [mD]

    # primary design choices
    inputs['m_dot'] = sweep_input['m_dot']  # [kg/s]
    inputs['r_f'] = sweep_input['r_f']  # [m]

    # additional parameters
    inputs['T_atm'] = sweep_input['T_atm']  # [C]
    inputs['p_atm'] = sweep_input['p_atm']  # [MPa]
    inputs['T_water'] = sweep_input['T_water']  # [C]
    inputs['p_water'] = sweep_input['p_water']  # [MPa]
    inputs['loss_mech'] = sweep_input['loss_mech']  # [-]
    inputs['loss_gen'] = sweep_input['loss_gen']  # [-]
    inputs['r_w'] = sweep_input['r_w']  # [m]
    inputs['epsilon'] = sweep_input['epsilon']  # [-]
    inputs['p_hydro_grad'] = sweep_input['p_hydro_grad']  # [MPa/km]
    inputs['p_frac_grad'] = sweep_input['p_frac_grad']  # [MPa/km]
    inputs['safety_factor'] = sweep_input['safety_factor']  # [-]
    inputs['T_grad_m'] = sweep_input['T_grad_m']  # [C/km]
    inputs['T_grad_b'] = sweep_input['T_grad_b']  # [C]
    inputs['loss_m_air'] = sweep_input['loss_m_air']  # [-]
    inputs['mach_limit'] = sweep_input['mach_limit']  # [-]
    inputs['t_pipe'] = sweep_input['t_pipe']  # [-]
    inputs['t_cement'] = sweep_input['t_cement']  # [-]
    inputs['t_insul'] = sweep_input['t_insul']  # [-]
    inputs['r_rock'] = sweep_input['r_rock']  # [-]
    inputs['k_cement'] = sweep_input['k_cement']  # [-]
    inputs['k_pipe'] = sweep_input['k_pipe']  # [-]
    inputs['k_insul'] = sweep_input['k_insul']  # [-]
    inputs['k_rock'] = sweep_input['k_rock']  # [-]
    inputs['depth_ocean'] = sweep_input['depth_ocean']  # [-]
    inputs['h_ocean'] = sweep_input['h_ocean']  # [-]
    inputs['T_ocean'] = sweep_input['T_ocean']  # [-]

    # ICAES parameters
    inputs['eta_pump'] = sweep_input['eta_pump']  # [-]
    inputs['ML_cmp1'] = sweep_input['ML_cmp1']  # [-]
    inputs['ML_cmp2'] = sweep_input['ML_cmp2']  # [-]
    inputs['ML_cmp3'] = sweep_input['ML_cmp3']  # [-]
    inputs['ML_exp1'] = sweep_input['ML_exp1']  # [-]
    inputs['ML_exp2'] = sweep_input['ML_exp2']  # [-]
    inputs['ML_exp3'] = sweep_input['ML_exp3']  # [-]
    inputs['delta_p_cmp23'] = sweep_input['delta_p_cmp23']  # [-]
    inputs['delta_p_exp12'] = sweep_input['delta_p_exp12']  # [-]

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
    xlsx_filename = 'user_inputs_general_monte_carlo.xlsx'  # Excel file with inputs
    sheet_names = ['geophysical']  # Excel sheet_names
    iterations = 10000  # number of runs per scenario
    ncpus = 6  # number of cpus to use

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
