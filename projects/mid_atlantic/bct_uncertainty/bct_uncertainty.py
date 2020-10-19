from caes import ICAES, monteCarloInputs
import pandas as pd
import numpy as np
from joblib import Parallel, delayed, parallel_backend
import time
import os
from math import log
from datetime import datetime


# =====================
# function to enable sizing for each entry in input file (XLSX_filename)
# =====================
def parameter_sweep(sweep_input, debug=True):
    start = time.time()

    if sweep_input['m_dot'] > 0.0 and sweep_input['r_f']  > 0.0:

        # create system
        inputs = ICAES.get_default_inputs()

        # uncertainty parameters - general
        inputs['T_grad_m'] = sweep_input['T_grad_m']  # [C/km]
        inputs['p_hydro_grad'] = sweep_input['p_hydro_grad']  # [MPa/km]
        inputs['p_frac_grad'] = sweep_input['p_frac_grad']  # [MPa/km]
        inputs['loss_m_air'] = sweep_input['loss_m_air']  # [-]

        # uncertainty parameters - location-specifc
        inputs['depth'] = sweep_input['depth_m']  # [m]
        inputs['h'] = sweep_input['thickness_m']  # [m]
        inputs['phi'] = sweep_input['porosity']  # [-]
        inputs['k'] = sweep_input['permeability_mD']  # [mD]

        # design inputs
        inputs['m_dot'] = sweep_input['m_dot']  # [kg/s]
        inputs['r_f'] = sweep_input['r_f']  # [m]

        # machine design parameters - modified based on depth
        inputs['ML_cmp1'] = sweep_input['ML_cmp1']  # [-]
        inputs['ML_cmp2'] = sweep_input['ML_cmp2']  # [-]
        inputs['ML_cmp3'] = sweep_input['ML_cmp3']  # [-]
        inputs['ML_cmp4'] = sweep_input['ML_cmp4']  # [-]
        inputs['ML_cmp5'] = sweep_input['ML_cmp5']  # [-]

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

        # all other parameters - taken as default

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
    else:
        single_output = sweep_input
    return single_output


# =====================
# main program
# =====================
if __name__ == '__main__':
    start = time.time()
    # ==============
    # user inputs
    # ==============
    sizing_results = "study_results.csv"
    duration_hr = 24
    capacity_MW = 150
    formations = ['MK1-3', 'LK1', 'UJ1']  # column name: "sheet_name"
    iterations = 100  # number of runs per location
    ncpus = 3  # default number of cpus to use

    # ==============
    # begin program
    # ==============
    # determine number of processors to use
    try:
        ncpus = int(os.getenv('NUM_PROCS'))  # try to use variable defined in sbatch script
    except:
        ncpus = ncpus  # otherwise default to this number of cores

    # read-in data
    df = pd.read_csv(sizing_results)

    # replace nan with 0.0
    df = df.fillna(0.0)

    # DataFrame to hold results
    all_outputs = pd.DataFrame()

    # ------------------
    # iterate through formations and save intermediate results
    # ------------------
    for count, formation in enumerate(formations):
        # select data of interest
        df2 = df[(df.loc[:, 'sheet_name'] == formation) &
                 (df.loc[:, 'duration_hr'] == duration_hr) &
                 (df.loc[:, 'capacity_MW'] == capacity_MW)]

        # create Monte Carlo simulation for each row in df2
        mc_inputs = pd.DataFrame()
        for ind in df2.index:
            # access data for this row
            row = df2.loc[ind, :]

            # create dataframe to hold distributions for each row
            df_row = pd.DataFrame(index=range(iterations))

            # ------------------------
            # apply distributions
            # ------------------------

            # temperature gradient (deg C /km) - Triangle
            left = 16.0/1000.0 # convert to deg C / ,
            mode = 23.0/1000.0
            right = 24.0/1000.0
            df_row.loc[:, 'T_grad_m'] = np.random.triangular(left, mode, right, size=iterations)

            # aquifer pressure gradient (MPa / km) - Triangle
            left = 9.42
            mode = 10.0
            right = 11.1
            df_row.loc[:, 'p_hydro_grad'] = np.random.triangular(left, mode, right, size=iterations)

            # fracture pressure gradient (MPa / km) - Uniform
            low = 13.6
            high = 15.8
            df_row.loc[:, 'p_frac_grad'] = np.random.uniform(low=low, high=high, size=iterations)

            # air leakage - Triangle
            left = 0.0/100.0 # convert from % to fraction
            mode = 3.5/100.0
            right = 20.0/100.0
            df_row.loc[:, 'loss_m_air'] = np.random.triangular(left, mode, right, size=iterations)

            # depth
            variation = 0.1
            low = (1.0 - variation) * row['depth_m']
            high = (1.0 + variation) * row['depth_m']
            df_row.loc[:, 'depth_m'] = np.random.uniform(low=low, high=high, size=iterations)

            # thickness
            variation = 0.2
            low = (1.0 - variation) * row['thickness_m']
            high = (1.0 + variation) * row['thickness_m']
            df_row.loc[:, 'thickness_m'] = np.random.uniform(low=low, high=high, size=iterations)

            # porosity
            mean = row['porosity']
            sigma = 0.05 / 100.0  # convert from % to fraction
            df_row.loc[:, 'porosity'] = np.random.normal(loc=mean, scale=sigma, size=iterations)

            # permeability
            mean = log(row['permeability_mD'])
            sigma = 2.448
            df_row.loc[:, 'permeability_mD'] = np.random.lognormal(mean=mean, sigma=sigma, size=iterations)

            # ------------------------
            # keep these parameters constant
            # ------------------------
            df_row.loc[:, 'm_dot'] = row['m_dot']
            df_row.loc[:, 'r_f'] = row['r_f']
            df_row.loc[:, 'X (m)'] = row['X (m)']
            df_row.loc[:, 'Y (m)'] = row['Y (m)']
            df_row.loc[:, 'sheet_name'] = row['sheet_name']
            df_row.loc[:, 'duration_hr'] = row['duration_hr']
            df_row.loc[:, 'capacity_MW'] = row['capacity_MW']

            # ------------------------
            # machinery parameters - depth dependent
            # ------------------------
            # compression - mass load per stage (ratio of water to air by mass)
            df_row.loc[:, 'ML_cmp1'] = 2.0
            df_row.loc[:, 'ML_cmp2'] = 1.5
            df_row.loc[:, 'ML_cmp3'] = 1.0
            df_row.loc[:, 'ML_cmp4'] = -1  # <0 - unused
            df_row.loc[:, 'ML_cmp5'] = -1  # <0 - unused

            # expansion - mass loading per stage
            df_row.loc[:, 'ML_exp1'] = 1.0
            df_row.loc[:, 'ML_exp2'] = 1.5
            df_row.loc[:, 'ML_exp3'] = 2.0
            df_row.loc[:, 'ML_exp4'] = -1  # <0 - unused
            df_row.loc[:, 'ML_exp5'] = -1  # <0 - unused

            # compression - pressure drop inbetween stages (fraction)
            df_row.loc[:, 'delta_p_cmp12'] = 0.0  # between stages 1 and 2
            df_row.loc[:, 'delta_p_cmp23'] = 0.02
            df_row.loc[:, 'delta_p_cmp34'] = -1  # <0 - unused
            df_row.loc[:, 'delta_p_cmp45'] = -1  # <0 - unused

            # compression - pressure drop inbetween stages (fraction)
            df_row.loc[:, 'delta_p_exp12'] = 0.02  # between stages 1 and 2
            df_row.loc[:, 'delta_p_exp23'] = 0.0
            df_row.loc[:, 'delta_p_exp34'] = -1  # <0 - unused
            df_row.loc[:, 'delta_p_exp45'] = -1  # <0 - unused

            if row['depth_m'] > 1500:  # change several
                # compression - mass load per stage (ratio of water to air by mass)
                df_row.loc[:, 'ML_cmp4'] = 0.5

                # expansion - mass loading per stage
                df_row.loc[:, 'ML_exp1'] = 0.5
                df_row.loc[:, 'ML_exp2'] = 1.0
                df_row.loc[:, 'ML_exp3'] = 1.5
                df_row.loc[:, 'ML_exp4'] = 2.0

                # compression - pressure drop inbetween stages (fraction)
                df_row.loc[:, 'delta_p_cmp34'] = 0.02

                # compression - pressure drop inbetween stages (fraction)
                df_row.loc[:, 'delta_p_exp23'] = 0.02
                df_row.loc[:, 'delta_p_exp34'] = 0.0

            # ------------------------
            # store distributions
            # ------------------------
            mc_inputs = mc_inputs.append(df_row)

        # reset index (appending messes up indices)
        mc_inputs = mc_inputs.reset_index()

        # count number of cases
        n_cases = mc_inputs.shape[0]

        # save model inputs
        savename = 'uncertainty_inputs' + str(count) + '.csv'
        mc_inputs.to_csv(savename)

        # run using parallelization
        with parallel_backend('multiprocessing', n_jobs=ncpus):
            output = Parallel(n_jobs=ncpus, verbose=5)(
                delayed(parameter_sweep)(mc_inputs.loc[index], debug=False)
                for index in range(n_cases))
        mc_outputs = pd.DataFrame(output)

        # save intermediate results
        savename = 'uncertainty_results' + str(count) + '.csv'
        mc_outputs.to_csv(savename)
        # group all outputs
        all_outputs = all_outputs.append(mc_outputs)

    # save all results
    all_outputs.to_csv('uncertainty_results_all.csv')

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