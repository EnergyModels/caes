from caes import monteCarloInputs
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================
# main program
# =====================
if __name__ == '__main__':
    # ==============
    # user inputs
    # ==============
    xlsx_filenames = ['user_inputs_location_monte_carlo.xlsx',
                      'prev_user_inputs_location_monte_carlo.xlsx']  # Excel file with inputs
    distributions = ['Updated', 'Previous']
    # sheet_names = ['PJM', 'NYISO', 'ISONE']  # Excel sheet_names
    sheet_names = ['PJM']  # Excel sheet_names
    iterations = 10000  # number of runs per scenario

    # ------------------
    # create sweep_inputs dataframe
    # ------------------
    df = pd.DataFrame()
    for xlsx_filename, distribution in zip(xlsx_filenames, distributions):
        for sheet_name in sheet_names:
            df_scenario = monteCarloInputs(xlsx_filename, sheet_name, iterations)
            df_scenario.loc[:, 'filename'] = xlsx_filename
            df_scenario.loc[:, 'distribution'] = distribution
            df = df.append(df_scenario)

    # reset index (appending messes up indices)
    df = df.reset_index()

    # ==============================
    # Plot distributions
    # ==============================

    # Set Color Palette
    colors = sns.color_palette("colorblind")
    # Set resolution for saving figures
    DPI = 300

    # Column width guidelines https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
    # Single column: 90mm = 3.54 in
    # 1.5 column: 140 mm = 5.51 in
    # 2 column: 190 mm = 7.48 i
    width = 7.48  # inches
    height = 5.5  # inches

    y_vars = ['depth', 'h', 'phi', 'k',
              'T_atm', 'T_water', 'p_hydro_grad', 'p_frac_grad',
              'T_grad_m', 'T_grad_b', 'loss_m_air']
    y_labels = ['Depth [m]', 'Thickness [m]', 'Porosity [-]', 'Permeability [mD]',
                'T_atm [C]', 'T_water [C]', 'p_hydro_grad [MPa/km]', 'p_frac_grad [MPa/km]',
                'T_grad [C/km]', 'T_grad0 [C]', 'Air loss [%]']
    y_converts = [1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0,
                  1000.0, 1.0, 100.0]
    legend = [False, False, False, False,
              False, False, False, False,
              False, False, True]

    for sheet_name in sheet_names:
        f, a = plt.subplots(3, 4)  # , sharey=True)
        a = a.ravel()

        # Set size
        f.set_size_inches(width, height)
        for ax, y_var, y_label, y_convert, leg in zip(a, y_vars, y_labels, y_converts, legend):
            df2 = df[df.loc[:, 'sheetname'] == sheet_name]
            df2.loc[:, y_var] = df2.loc[:, y_var] * y_convert
            if y_var == 'k':
                sns.histplot(data=df2, x=y_var, ax=ax, hue='distribution', multiple='dodge', element='step', fill=False,
                             log_scale=True,
                             legend=leg)
            else:
                sns.histplot(data=df2, x=y_var, ax=ax, hue='distribution', multiple='dodge', element='step', fill=False,
                             legend=leg)
            ax.set_xlabel(y_label)
            ax.set_ylim(top=1000)

        # a[10].legend(bbox_to_anchor=(1.0, 0.5), ncol=1)

        # Save Figure
        savename = sheet_name + '_distribution.png'
        plt.tight_layout()
        plt.savefig(savename, dpi=DPI)
        # plt.close()

df.to_csv('distribution_comparison.csv')
