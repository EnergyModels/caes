from caes import CAES
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pwr_incs = [100, 500, 1000, 5000]


# =====================
# Function to enable parameter sweep
# =====================
def parameterSweep(dataFile, solarCapacity, battSize, inputs, rampRate, index):
    # Record time to solve
    t0 = time.time()

    # Load_Data - Expected Columns (units): DatetimeUTC (UTC format), t (min), dt (min), demand (MW), solar (MW)
    data = pd.read_csv(dataFile)

    # Solar Plant - All inputs are optional (default values shown below)
    solar = Solar(plantType='PV', capacity=solarCapacity, cost_install=2004., cost_OM_fix=22.02)

    # Battery Storage - All inputs are optional (default values shown below)
    batt = Battery(capacity=battSize, rateMax=battSize, roundTripEff=85.0, cost_install=2067., cost_OM_fix=35.6,
                   initCharge=100.0)

    # Fuel - All inputs are optional (default values shown below)
    fuel = Fuel(fuelType='NATGAS', cost=10.58, emissions=0.18)

    # Create power plant
    # 1 - create pandas series of power plant characteristics
    plant_inputs = defaultInputs(plantType='CCGT')  # Start with CCGT default inputs and then adjust to specific case
    plant_inputs.capacity = 51.3  # MW
    plant_inputs.plantType = inputs.sheetname
    plant_inputs.Eff_A = inputs.Eff_A
    plant_inputs.Eff_B = inputs.Eff_B
    plant_inputs.Eff_C = inputs.Eff_C
    plant_inputs.maxEfficiency = inputs.maxEfficiency
    plant_inputs.rampRate = rampRate
    plant_inputs.minRange = inputs.minRange
    plant_inputs.cost_install = inputs.cost_install
    plant_inputs.cost_OM_fix = inputs.cost_OM_fix
    plant_inputs.cost_OM_var = inputs.cost_OM_var
    plant_inputs.co2CaptureEff = inputs.co2CaptureEff

    # 2 - create power plant
    plant = PowerPlant(plant_inputs)

    # Create HRES (controller is built-in), data and plant are only required inputs
    # all other components will revert to default if not specified
    hres = HRES(data, plant, solar=solar, batt=batt, fuel=fuel, i=0.02, n=20)

    # Run Simulation
    results = hres.run()

    # Display Elapsed Time
    t1 = time.time()
    print("Time Elapsed: " + str(round(t1 - t0, 2)) + " s")

    # Combine inputs and results into output and then return
    inputs = inputs.drop('rampRate')
    s_solarCapacity = pd.Series([solarCapacity], index=['solarCapacity_MW'])
    s_battSize = pd.Series([battSize], index=['battSize_MW'])
    s_rampRate = pd.Series([rampRate], index=['rampRate'])
    output = pd.concat([inputs, s_solarCapacity, s_battSize, s_rampRate, results], axis=0)
    return output


attributes = ['pwr_inc', 'pmin', 'PR', 'RTE']
df = pd.DataFrame(columns=attributes)
pmins = [1e3]  # [0.5e3, 1.0e3, 1.5e3]
PRs = np.arange(1.2, 2.0, 0.1)

for pwr_inc in pwr_incs:
    for pmin in pmins:
        for PR in PRs:
            inputs = CAES.get_default_inputs()
            inputs['p_store_min'] = pmin
            inputs['p_store_init'] = pmin
            inputs['p_store_max'] = pmin * PR
            system = CAES(inputs=inputs)
            system.single_cycle(pwr_inc)
            results = system.analyze_performance()

            s = pd.Series(index=attributes)
            s['pwr_inc'] = pwr_inc
            s['pmin'] = pmin / 1000.0
            s['PR'] = PR
            s['RTE'] = results['RTE']
            df = df.append(s, ignore_index=True)
            print('pwr_inc:' + str(pwr_inc))
            print('pmin:' + str(pmin))
            print('PR:' + str(PR))

sns.scatterplot(x='PR', y='RTE', hue='pmin', style='pwr_inc', data=df)
plt.savefig('demo.png', dpi=600)
