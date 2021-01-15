import pandas as pd

# ------------------- #
# inputs
# ------------------- #
results_file = 'uncertainty_results_all.csv'
formations = ['LK1', 'MK1-3', 'UJ1']  # needs to be present in the sheet_name column of the results_file
ocean_data_files = ['LK1_ocean_data.xls', 'MK1_3_ocean_data.xls', 'UJ1_ocean_data.xls']
sizing_file = 'study_results.csv'


# ------------------- #
# begin program
# ------------------- #
# read-in results
df_results = pd.read_csv(results_file)
df_sizing = pd.read_csv(sizing_file)

# fill in nan values
df_results = df_results.fillna(0.0)

# create dataframe to hold all results
df_all = pd.DataFrame()

# analyze each formation separately
for formation, ocean_data_file in zip(formations, ocean_data_files):

    # read-in ocean_data
    df_ocean = pd.read_excel(ocean_data_file)

    # iteratre through each entry in df_ocean
    for ID in df_ocean.OBJECTID.unique():
        # select current entry in df_ocean and get X and Y data
        i = df_ocean.loc[:, 'OBJECTID'] == ID
        X_m = df_ocean.loc[i, 'X_m'].values[0]
        Y_m = df_ocean.loc[i, 'Y_m'].values[0]

        # select relevant entries in df_results and sizing
        ind = (df_results.loc[:, 'sheet_name'] == formation) & (df_results.loc[:, 'X (m)'] == X_m) & (
                    df_results.loc[:, 'Y (m)'] == Y_m)
        ind2 = (df_sizing.loc[:, 'sheet_name'] == formation) & (df_sizing.loc[:, 'X (m)'] == X_m) & (
                    df_sizing.loc[:, 'Y (m)'] == Y_m)

        # store formation name
        df_ocean.loc[i, 'formation'] = formation

        # analyze and create new entries in df_ocean
        # RTE
        df_ocean.loc[i, 'RTE_min'] = df_results.loc[ind, 'RTE'].min()
        df_ocean.loc[i, 'RTE_mean'] = df_results.loc[ind, 'RTE'].mean()
        df_ocean.loc[i, 'RTE_max'] = df_results.loc[ind, 'RTE'].max()

        # Power
        df_ocean.loc[i, 'kW_out_min'] = df_results.loc[ind, 'kW_out_avg'].min()
        df_ocean.loc[i, 'kW_out_mean'] = df_results.loc[ind, 'kW_out_avg'].mean()
        df_ocean.loc[i, 'kW_out_max'] = df_results.loc[ind, 'kW_out_avg'].max()

        # Storage
        df_ocean.loc[i, 'kWh_out_min'] = df_results.loc[ind, 'kWh_out'].min()
        df_ocean.loc[i, 'kWh_out_mean'] = df_results.loc[ind, 'kWh_out'].mean()
        df_ocean.loc[i, 'kWh_out_max'] = df_results.loc[ind, 'kWh_out'].max()

        # Feasibility
        n_entries = sum(ind)
        n_fail = sum(df_results.loc[ind, 'RTE'] == 0.0)
        df_ocean.loc[i, 'feasible_fr'] = 1.0 - n_fail / n_entries
        df_ocean.loc[i, 'infeasible_fr'] = n_fail / n_entries

        # Sizing
        df_ocean.loc[i, 'm_dot'] = df_sizing.loc[ind2, 'm_dot']
        df_ocean.loc[i, 'r_f'] = df_sizing.loc[ind2, 'r_f']

    # save results to new csv
    savename = formation + '_analysis.csv'
    df_ocean.to_csv(savename)

    # save formation results into all df
    df_all = df_all.append(df_ocean)

# save results to new csv
savename = 'all_analysis.csv'
df_all.to_csv(savename)
