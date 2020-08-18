import pandas as pd

df = pd.read_csv('study_results.csv')

# error handling
df = df.fillna(0.0)

# split into 3 dataframes
df_LK = df.loc[df.loc[:, 'sheet_name'] == 'LK1', :]
df_MK = df.loc[df.loc[:, 'sheet_name'] == 'MK1-3', :]
df_UJ = df.loc[df.loc[:, 'sheet_name'] == 'UJ1', :]

# save each results
df_LK.to_csv('results_LK1.csv')
df_MK.to_csv('results_MK1-3.csv')
df_UJ.to_csv('results_UJ1.csv')
