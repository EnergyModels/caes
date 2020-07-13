# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
"""
BLIS - Balancing Load of Intermittent Solar:
A characteristic-based transient power plant model

Copyright (C) 2020. University of Virginia Licensing & Ventures Group (UVA LVG). All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
import pandas as pd
import numpy as np


# =============================================================================#
# Create MonteCarlo Inputs
# =============================================================================#
def monteCarloInputs(filename, sheetname, iterations):
    # Read Excel with inputs
    df_xls = pd.read_excel(filename, sheet_name=sheetname, index_col=0)

    # Create Dataframe to hold inputs
    rows = range(iterations)
    parameters1 = df_xls.index.values
    parameters2 = np.append('sheetname', parameters1)
    df = pd.DataFrame(data=0.0, index=rows, columns=parameters2)

    # Create Inputs
    for param in parameters1:

        dist_type = df_xls.loc[param]["Distribution"]

        # Constants
        if dist_type == "constant" or dist_type == "Constant" or dist_type == "C":
            avg = df_xls.loc[param]["Average"]
            df.loc[:][param] = avg

        # Uniform Distributions
        elif dist_type == "uniform" or dist_type == "Uniform" or dist_type == "U":
            low = df_xls.loc[param]["Low"]
            high = df_xls.loc[param]["High"]
            df.loc[:][param] = np.random.uniform(low=low, high=high, size=iterations)

        # Normal Distributions
        elif dist_type == "normal" or dist_type == "Normal" or dist_type == "N":
            avg = df_xls.loc[param]["Average"]
            stdev = df_xls.loc[param]["Stdev"]
            df.loc[:][param] = np.random.normal(loc=avg, scale=stdev, size=iterations)

        # LogNormal Distributions
        elif dist_type == "lognormal" or dist_type == "Lognormal" or dist_type == "LN":
            avg = df_xls.loc[param]["Average"]
            stdev = df_xls.loc[param]["Stdev"]
            df.loc[:][param] = np.random.lognormal(mean=avg, sigma=stdev, size=iterations)

        # Traingular Distributions
        elif dist_type == "triangle" or dist_type == "Triangle" or dist_type == "T":
            left = df_xls.loc[param]["Low"]
            mode = df_xls.loc[param]["Average"]
            right = df_xls.loc[param]["High"]
            df.loc[:][param] = np.random.triangular(left, mode, right, size=iterations)
    df.loc[:, 'sheetname'] = sheetname
    return df


# =============================================================================#
# Use MonteCarlo Inputs to Create Baselines
# =============================================================================#
def baselineInputs(filename, sheetname):
    # Read Excel with inputs
    df_xls = pd.read_excel(filename, sheet_name=sheetname, index_col=0)

    # Create series to hold inputs
    parameters1 = df_xls.index.values
    parameters2 = np.append('sheetname', parameters1)
    s = pd.Series(data=0.0, index=parameters2)

    # Create Inputs
    for param in parameters1:
        s.loc[param] = df_xls.loc[param]["Average"]

    s.loc['sheetname'] = sheetname
    return s
