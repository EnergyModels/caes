import os
import pandas as pd

case_dict = {'best_case': 'n=1.04', 'expected_case': 'n=1.1', 'worst_case': 'n=1.21'}

wrkdir = os.getcwd()
os.chdir('..')
rootdir = os.getcwd()

# initialize dataframe to hold all results
df = pd.DataFrame()

# iterate through directories and store results
for case in case_dict.keys():
    os.chdir(case)
    df_case = pd.read_csv('uncertainty_results_all.csv')
    df_case.loc[:, 'case'] = case
    df = df.append(df_case, ignore_index=True)
    os.chdir(rootdir)

# reset indices - appending messes with indices
df.reset_index()

# save
os.chdir(wrkdir)
df.to_csv('combined_results.csv')
