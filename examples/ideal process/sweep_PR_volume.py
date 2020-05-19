from caes import CAES, plot_series
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
    inputs = CAES.get_default_inputs()
    inputs['steps'] = sweep_input['steps']  # [kPa]
    inputs['p_store_min'] = sweep_input['p_min']  # [kPa]
    inputs['p_store_init'] = sweep_input['p_min']  # [kPa]
    inputs['p_store_max'] = sweep_input['p_max']  # [kPa]
    inputs['eta_storage'] = sweep_input['eta_storage']  # [-]
    inputs['V_res'] = sweep_input['V_res']  # [m3]
    inputs['phi'] = sweep_input['phi']  # porosity [-]
    inputs['Slr'] = sweep_input['Slr']  # liquid residual fraction [-]
    system = CAES(inputs=inputs)

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
    V_ress = np.array([1.0e3, 5.0e3, 1.0e4, 5.0e4, 1.0e5, 5.0e5, 1.0e6])  # reservoir volume [m3]
    PRs = np.arange(1.1, 2.1, 0.1)  # pressure ratio [-]
    phis = np.array([1.0])  # porosity [-]
    Slrs = np.array([0.0])  # liquid residual fraction [-]
    # kept at default values
    steps = np.array([CAES.get_default_inputs()['steps']])  # number of solution time steps [-]
    p_mins = np.array([CAES.get_default_inputs()['p_store_min']])  # minimum pressure [kPa]
    eta_storages = np.array([CAES.get_default_inputs()['eta_storage']])  # storage efficiency [fr]

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
    df.loc[:, 'Efficiency [%]'] = df.loc[:, 'RTE'] * 100.0
    df.loc[:, 'Energy [MWh]'] = df.loc[:, 'kWh_out'] * 1.0e-3
    df.loc[:, 'Volume [1000 m3]'] = df.loc[:, 'V_res'] * 1.0e-3
    df.loc[:, 'Pressure ratio [-]'] = round(df.loc[:, 'PR'], 2)

    # Set Color Palette
    colors = sns.color_palette("colorblind")
    palette = "colorblind"
    # Set resolution for saving figures
    DPI = 600
    # set style
    sns.set_style('white')
    sns.set_context('paper')

    sns.lineplot(data=df, x='Volume [1000 m3]', y='Efficiency [%]', hue='Pressure ratio [-]', legend='full',
                 palette=palette)
    plt.savefig('sweep_PR_volume1.png', dpi=DPI)
    plt.close()

    sns.lineplot(data=df, x='Volume [1000 m3]', y='Energy [MWh]', hue='Pressure ratio [-]', legend='full',
                 palette=palette)
    plt.savefig('sweep_PR_volume2.png', dpi=DPI)
    plt.close()

    sns.lineplot(data=df, x='Pressure ratio [-]', y='Efficiency [%]', hue='Volume [1000 m3]', legend='full',
                 palette=palette)
    plt.savefig('sweep_PR_volume3.png', dpi=DPI)
    plt.close()

    sns.lineplot(data=df, x='Pressure ratio [-]', y='Energy [MWh]', hue='Volume [1000 m3]', legend='full',
                 palette=palette)
    plt.savefig('sweep_PR_volume4.png', dpi=DPI)
    plt.close()
