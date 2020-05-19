from caes import ICAES, plot_series
import pandas as pd
import numpy as np
from joblib import Parallel, delayed, parallel_backend
import os
import time
import seaborn as sns
import matplotlib.pyplot as plt


# =====================
# function to enable parameter sweep
# =====================
def parameter_sweep(sweep_input):
    start = time.time()

    # create system
    inputs = ICAES.get_default_inputs()
    inputs['steps'] = sweep_input['steps']  # [kPa]
    inputs['p_store_min'] = sweep_input['p_min']  # [kPa]
    inputs['p_store_init'] = sweep_input['p_min']  # [kPa]
    inputs['p_store_max'] = sweep_input['p_max']  # [kPa]
    inputs['eta_storage'] = sweep_input['eta_storage']  # [-]
    inputs['V_res'] = sweep_input['V_res']  # [m3]
    inputs['phi'] = sweep_input['phi']  # porosity [-]
    inputs['Slr'] = sweep_input['Slr']  # liquid residual fraction [-]
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
    # ==============
    # user inputs
    # ==============
    savename = "sweep_soln_settings.png"
    # ------------------
    # integer inputs
    # ------------------
    ncpus = 3  # int(os.getenv('NUM_PROCS'))
    # ------------------
    # numpy array inputs
    # ------------------
    # investigated
    steps = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 8.0, 10.0, 25.0, 50.0, 75.0, 100.0, 250.0, 500.0, 750.0,
                      1000.0])  # number of solution time steps [-]

    # kept at default values
    p_mins = np.array([ICAES.get_default_inputs()['p_store_min']])  # minimum pressure [kPa]
    PRs = np.array(
        [ICAES.get_default_inputs()['p_store_max'] / ICAES.get_default_inputs()['p_store_min']])  # pressure ratio [-]
    eta_storages = np.array([ICAES.get_default_inputs()['eta_storage']])  # storage efficiency [fr]
    V_ress = np.array([ICAES.get_default_inputs()['V_res']])  # reservoir volume [m3]
    phis = np.array([ICAES.get_default_inputs()['phi']])  # porosity [-]
    Slrs = np.array([ICAES.get_default_inputs()['Slr']])  # liquid residual fraction [-]

    # ==============
    # run simulations
    # ==============

    # prepare dataframe to store inputs
    attributes = ['steps', 'p_min', 'PR', 'p_max', 'eta_storage', 'V_res', 'phi', 'Slr']
    sweep_inputs = pd.DataFrame(columns=attributes)

    count = 0
    for step in steps:
        for p_min in p_mins:
            for PR in PRs:
                for eta_storage in eta_storages:
                    for V_res in V_ress:
                        for phi in phis:
                            for Slr in Slrs:
                                sweep_inputs.loc[count, 'steps'] = step
                                sweep_inputs.loc[count, 'p_min'] = p_min
                                sweep_inputs.loc[count, 'PR'] = PR
                                sweep_inputs.loc[count, 'p_max'] = p_min * PR
                                sweep_inputs.loc[count, 'eta_storage'] = eta_storage
                                sweep_inputs.loc[count, 'V_res'] = V_res
                                sweep_inputs.loc[count, 'phi'] = phi
                                sweep_inputs.loc[count, 'Slr'] = Slr
                                count = count + 1
    n_cases = sweep_inputs.shape[0]

    # run each case using parallelization
    with parallel_backend('multiprocessing', n_jobs=ncpus):
        output = Parallel(n_jobs=ncpus, verbose=5)(
            delayed(parameter_sweep)(sweep_inputs.loc[index])
            for index in
            range(n_cases))
    df = pd.DataFrame(output)

    # ==============
    # plot results
    # ==============
    x_var = 'steps'
    x_label = 'Steps [-]'
    x_convert = 1.0

    y_vars = ['kWh_in', 'kWh_out', 'RTE', 'solve_time']
    y_labels = ['Energy in\n[MWh]', 'Energy out\n[MWh]', 'Round trip efficiency\n[%]', 'Solve time\n[s]']
    y_converts = [1.0e-3, 1.0e-3, 100.0, 1.0]

    plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts, scale='log')
    plt.savefig(savename, dpi=600)
    plt.close()
