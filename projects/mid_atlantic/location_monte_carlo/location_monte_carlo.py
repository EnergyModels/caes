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

    # create system
    inputs = ICAES.get_default_inputs()
    # user inputs
    # primary geophysical parameters
    inputs['depth'] = sweep_input['depth']  # [m]
    inputs['h'] = sweep_input['h']  # [m]
    inputs['phi'] = sweep_input['phi']  # [-]
    inputs['k'] = sweep_input['k']  # [mD]

    # current guess/iteration
    inputs['m_dot'] = sweep_input['m_dot']   # [kg/s]
    inputs['r_f'] = sweep_input['r_f']   # [m]

    # held constant
    inputs['p_atm'] = sweep_input['p_atm']  # [MPa]
    inputs['p_water'] = sweep_input['p_water']  # [MPa]

    # additional geophysical parameters
    inputs['T_atm'] = sweep_input['T_atm']  # [C]
    inputs['T_water'] = sweep_input['T_atm']  # [C]
    inputs['p_hydro_grad'] = sweep_input['p_hydro_grad']  # [MPa/km]
    inputs['p_frac_grad'] = sweep_input['p_frac_grad']  # [MPa/km]
    inputs['T_grad_m'] = sweep_input['T_grad_m']  # [C/km]
    inputs['T_grad_b'] = sweep_input['T_grad_b']  # [C]
    inputs['loss_m_air'] = sweep_input['loss_m_air']  # [-]

    # primary design choices - held constant
    inputs['r_w'] = sweep_input['r_w']  # [m]
    inputs['epsilon'] = sweep_input['epsilon']  # [-]
    inputs['safety_factor'] = sweep_input['safety_factor']  # [-]
    inputs['loss_mech'] = sweep_input['loss_mech']  # [-]
    inputs['loss_gen'] = sweep_input['loss_gen']  # [-]
    inputs['mach_limit'] = sweep_input['mach_limit']  # [-]
    inputs['eta_pump'] = sweep_input['eta_pump']  # [-]

    inputs['ML_cmp1'] = sweep_input['ML_cmp1']  # [-]
    inputs['ML_cmp2'] = sweep_input['ML_cmp2']  # [-]
    inputs['ML_cmp3'] = sweep_input['ML_cmp3']  # [-]
    inputs['ML_cmp3'] = sweep_input['ML_cmp3']  # [-]
    inputs['ML_cmp4'] = sweep_input['ML_cmp4']  # [-]

    inputs['ML_exp1'] = sweep_input['ML_exp1']  # [-]
    inputs['ML_exp2'] = sweep_input['ML_exp2']  # [-]
    inputs['ML_exp3'] = sweep_input['ML_exp3']  # [-]
    inputs['ML_exp4'] = sweep_input['ML_exp4']  # [-]
    inputs['ML_exp5'] = sweep_input['ML_exp5']  # [-]

    inputs['delta_p_cmp12'] = sweep_input['delta_p_cmp12']  # [-]
    inputs['delta_p_cmp23'] = sweep_input['delta_p_cmp23']  # [-]
    inputs['delta_p_cmp34'] = sweep_input['delta_p_cmp34']  # [-]
    inputs['delta_p_cmp45'] = sweep_input['delta_p_cmp45']  # [-]

    inputs['delta_p_exp12'] = sweep_input['delta_p_exp12']  # [-]
    inputs['delta_p_exp23'] = sweep_input['delta_p_exp23']  # [-]
    inputs['delta_p_exp34'] = sweep_input['delta_p_exp34']  # [-]
    inputs['delta_p_exp45'] = sweep_input['delta_p_exp45']  # [-]


    system = ICAES(inputs=inputs)

    # run single cycle and analyze
    system.single_cycle()
    results = system.analyze_performance()

    end = time.time()
    results['solve_time'] = end - start

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
    xlsx_filename = 'user_inputs_location_monte_carlo.xlsx'  # Excel file with inputs
    sheet_names = ['PJM', 'NYISO', 'ISONE']  # Excel sheet_names
    iterations = 10000  # number of runs per scenario
    ncpus = 3  # number of cpus to use

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
