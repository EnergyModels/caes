import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# common inputs
resolution = 500
filename = "sensitivity_results.csv"
directories = ['PJM', 'NYISO', 'ISONE',
               'MK_5', 'MK_10', 'MK_15', 'MK_20',
               'LK_10', 'LK_15', 'LK_20', 'LK_25', 'LK_30',
               'UJ_20', 'UJ_25', 'UJ_30']  # Excel sheet_names

directories = ['MK_3', 'LK_1', 'LK_5']  # Excel sheet_names

# dictionary to rename sensitivty variables
sens_var_rename = {'steps': 'Solver steps',
                   'T_atm': 'Atmospheric temperature, $T_{atm}$ ',
                   'p_atm': 'Atmospheric pressure, $p_{atm}$',
                   'T_water': 'Water temperature',
                   'p_water': 'Water pressure',
                   'fuel_HHV': 'Fuel HHV',
                   'fuel_CO2': 'Fuel Emission Factor',
                   'loss_mech': 'Mechanical loss, $(1 - \eta_{mech})$ ',
                   'loss_gen': 'Generator loss, $(1 - \eta_{gen})$',
                   'r_w': 'Well radius, $r_w$ ',
                   'epsilon': 'Pipe roughness, $\epsilon$ ',
                   'depth': 'Depth, $z$ ',
                   'p_hydro_grad': 'Aquifer pressure gradient, $\partial p_{aq} / \partial z}$',
                   'p_frac_grad': 'Fracture pressure gradient, $\partial p_f / \partial z}$',
                   'safety_factor': 'Safety Factor, $SF$',
                   'T_grad_m': 'Geothermal gradient, $\partial T / \partial z}$',
                   'T_grad_b': 'Geothermal intercept, $T_0$',
                   'r_f': 'Formation radius',
                   'h': 'Thickness, $h$',
                   'phi': 'Porosity, $\phi$',
                   'slr': 'Liquid residual fraction',
                   'k': 'Permeability, $k$',
                   'loss_m_air': 'Air leakage, $\.{m}_{leak}$',
                   'm_dot': 'Mass flow rate, $\.{m}$',
                   'mach_limit': 'Mach limit',
                   't_pipe': 'Pipe wall thickness',
                   't_cement': 'Cement thickness',
                   't_insul': 'Insulation thickness',
                   'r_rock': 'Rock radius',
                   'k_cement': 'Cement thermal conductivity',
                   'k_pipe': 'Pipe thermal conductivity',
                   'k_insul': 'Insulation conductivity',
                   'k_rock': 'Rock thermal conductivity',
                   'depth_ocean': 'Ocean depth',
                   'h_ocean': 'Ocean convection coefficient',
                   'T_ocean': 'Ocean temperature',
                   'n_cmp1': 'Compressor Polytropic Index',
                   'n_exp1': 'Expander Polytropic Index'}

wrkdir = os.getcwd()

for directory in directories:

    # move to folder with results
    result_dir = os.path.join(wrkdir, directory)
    os.chdir(result_dir)

    for plt_num in range(3):
        # ------------------------
        # plot version inputs
        # ------------------------
        if plt_num == 0:  # Select
            savename = 'sensitivity_results_select.png'
            variables = ['RTE', 'kWh_out', 'kW_out_avg']
            varLabels = ['Round Trip Efficiency (%)', 'Energy Out (MWh)', 'Average Power Out (MW)']
            conversions = [100.0, 1e-3, 1e-3]
            ncols = 1
            nrows = 3
            n_display = 5  # max number of variables to display

            width = 4.5  # inches
            height = 5.5  # inches
        elif plt_num == 1:  # Select
            savename = 'sensitivity_results_eff.png'
            variables = ['RTE']
            varLabels = ['RTE [%]']
            conversions = [100.0]
            ncols = 1
            nrows = 1
            n_display = 15

            width = 4.5  # inches
            height = 4.5  # inches
        else:  # All
            savename = 'sensitivity_results_all.png'
            variables = ['RTE', 'kg_water_per_kWh', 'kWh_in', 'kWh_out', 'kW_in_avg', 'kW_out_avg']
            varLabels = ['Round Trip Efficiency (%)', 'Water Use (kg/kWh)', 'Energy In (MWh)', 'Energy Out (MWh)',
                         'Average Power In (MW)', 'Average Power Out (MW)']
            conversions = [100.0, 1.0, 1e-3, 1e-3, 1e-3, 1e-3]
            ncols = 2
            nrows = 3
            n_display = 5  # max number of variables to display

            width = 7.48  # inches
            height = 5.5  # inches

        # ------------------------
        # Begin program
        # ------------------------

        # --------
        # Pre-processing
        # --------

        # Read-in csv
        df = pd.read_csv(filename)

        # Convert units
        for var, convert in zip(variables, conversions):
            df.at[:, var] = df.loc[:, var] * convert

        # Keep a copy of the baseline
        baseline = df.loc[0].copy()

        # Remove bad values (0 and null values) and set equal to the baseline
        for var in variables:
            # Zero values
            ind = df.loc[:, var] == 0.0
            df.at[ind, var] = baseline[var]

            # Null values
            ind = df.loc[:, var].isnull()
            df.at[ind, var] = baseline[var]

        # Normalize results wrt baseline
        for var in variables:
            df.at[1:, var] = df.loc[1:, var] - df.loc[0, var]

        # Remove baseline from dataframe
        df = df.drop([0])

        # Sort data so that the same permutation cases are adjacent and start with negative multiplier
        df = df.sort_values(by=['sensitivity_var', 'permutation'])

        # Create dictionary to hold dataframes
        results = {}

        # Create new DataFrame to hold sorted results
        cols = ['variable', 'low', 'high', 'abs']
        for var in variables:
            results[var] = pd.DataFrame(columns=cols)

        # fill-in data
        i = 1
        while i < len(df):

            for var in variables:
                s = pd.Series()
                s['variable'] = sens_var_rename[df.loc[i, 'sensitivity_var']]
                s['high'] = df.loc[i, var]  # + baseline[var]
                s['low'] = df.loc[i + 1, var]  # + baseline[var]
                s['abs'] = max(abs(df.loc[i, var]), abs(df.loc[i + 1, var]))
                results[var] = results[var].append(s, ignore_index=True)

            # Increment i
            i = i + 2

        # --------
        # Sort Results by abs col (absolute value of largest change)
        # --------
        for var in variables:
            results[var] = results[var].sort_values(by=['abs'], ascending=False)

            # Reset index
            results[var] = results[var].reset_index(drop=True)

        # --------
        # Create Plots
        # --------

        custom_palette = [(0.380, 0.380, 0.380), (0.957, 0.451, 0.125), (.047, 0.149, 0.361),
                          (0.847, 0.000, 0.067)]  # Custom palette

        # Initialize the matplotlib figure
        f, a = plt.subplots(ncols=ncols, nrows=nrows, squeeze=False)
        axes = a.ravel()

        # Set size
        # Column width guidelines
        # https://www.elsevier.com/authors/author-schemas/artwork-and-media-instructions/artwork-sizing
        # Single column: 90mm = 3.54 in
        # 1.5 column: 140 mm = 5.51 in
        # 2 column: 190 mm = 7.48 i

        f.set_size_inches(width, height)

        # Set style and context
        sns.set_style("white", {"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
        sns.set_context("paper")
        sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

        for var, varLabel, ax in zip(variables, varLabels, axes):
            n_cases = min(len(results[var]), n_display)

            # Plot the low side
            # sns.barplot(x="low", y="variable", data=results[var].loc[:n_cases], orient="h", label="-10%",
            #             color=custom_palette[2], ax=ax)  # Blue
            ax.barh(y=np.arange(n_cases), width=results[var].loc[:n_cases - 1].low, label="-10%", left=baseline[var],
                    color=custom_palette[2], tick_label=results[var].loc[:n_cases - 1].variable)

            # Plot the high side
            # sns.barplot(x="high", y="variable", data=results[var].loc[:n_cases], label="+10%",
            #             color=custom_palette[1], ax=ax)  # Orange

            ax.barh(y=np.arange(n_cases), width=results[var].loc[:n_cases - 1].high, label="+10%", left=baseline[var],
                    color=custom_palette[1], tick_label=results[var].loc[:n_cases - 1].variable)

            # y_orig = ax.get_yticklabels()
            # ax.set_yticklabels(results[var].loc[:n_cases - 1].variable)
            # ax.set_yticklabels(['a', 'b', 'c', 'd', 'e'])

            ax.invert_yaxis()

            # Remove spines
            sns.despine(left=True, bottom=True, ax=ax)

            # Adjust ticks to show perturbation + mean value
            ax.xaxis.set_major_locator(plt.MaxNLocator(4))  # Ensure 3 ticks
            # ax.xaxis.set_major_locator(plt.MaxNLocator(n_cases))  # Ensure 3 ticks

            # # locs, labels = plt.xticks()
            # labels = ax.get_xticklabels()
            # for i in range(len(labels)):
            #     a = float(baseline[var])
            #     b = labels[i]._x
            #     # b = float(labels[i].get_text())
            #     c = round(a+b, 2)
            #     label = str(c)
            #     labels[i].set_text(label)
            #     print(i)
            #     # print(val)
            #     print(label)
            # ax.set_xticklabels(labels)

            # Set label
            ax.set_xlabel(varLabel, fontweight='bold')
            ax.set_ylabel('')

        # legend
        if plt_num == 0:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), ncol=2)
        elif plt_num == 1:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
        else:
            ax.legend(loc='upper right', bbox_to_anchor=(-0.1, -0.3), ncol=2)

        # Adjust layout
        # plt.subplots_adjust(hspace=0.2, wspace=0.5, bottom=0.1)
        plt.tight_layout()

        # Save plot
        f.savefig(savename, dpi=resolution, bbox_inches="tight")
        plt.close()
