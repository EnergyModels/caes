import pandas as pd
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import log, pi
from .pressure_drop import aquifer_dp, pipe_fric_dp, pipe_grav_dp
from .plot_functions import plot_series
import matplotlib.pyplot as plt


# references
#
# Allen et al. 1983 -
#
# Battelle 2019 - Battelle, Delaware Geological Survey, Maryland Geological Survey, Pennsylvania Geological Survey,
# United States Geological Survey, Lamont-Doherty Earth Observatory at Columbia University, and Rutgers University.
# Mid-Atlantic U.S. Offshore Carbon Storage Resource Assessment Project Task 6 Risk Factor Analysis Report. DOE
# Cooperative Agreement No. DE-FE0026087. September 2019.
# https://edx.netl.doe.gov/dataset/mid-atlantic-final-technical-report
#
# Fukai et al. 2020 - Fukai, I., Keister, L., Ganesh, P.R., Cumming, L., Fortin, W., and Gupta, N., 2020, "Carbon
# dioxide storage resource assessment of Cretaceous- and Jurassic-age sandstones in the Atlantic offfshore region of the
# northeastern United States", Environmental Geosciences, V. 27, No. 1, 25-47.
# https://doi.org/10.1306/eg.09261919016
#


class CAES:

    def get_default_inputs():
        attributes = ['debug', 'steps',
                      'include_air_leakage', 'include_aquifer_dp',
                      'include_thermal_gradient', 'include_pipe_dp_gravity',
                      'include_pipe_dp_friction', 'include_pipe_heat_transfer',
                      'T_atm', 'p_atm', 'T_water', 'p_water', 'fuel_HHV', 'fuel_CO2',
                      'loss_mech', 'loss_gen',
                      'r_w', 'epsilon', 'depth',
                      'p_hydro_grad', 'p_frac_grad', 'safety_factor',
                      'T_grad_m', 'T_grad_b',
                      'r_f', 'h', 'phi', 'Slr', 'k', 'loss_m_air', 'm_dot', 'mach_limit']
        inputs = pd.Series(index=attributes)

        inputs['debug'] = False  # debug
        inputs['steps'] = 100.0  # number of steps to use in single cycle simulation

        # options to include/exclude various loss mechanisms
        inputs['include_air_leakage'] = True
        inputs['include_aquifer_dp'] = True
        inputs['include_thermal_gradient'] = True
        inputs['include_pipe_dp_gravity'] = True
        inputs['include_pipe_dp_friction'] = True
        inputs['include_pipe_heat_transfer'] = False

        inputs['T_atm'] = 16.85  # [deg C] 290 K, yearly average for Virginia coast
        inputs['p_atm'] = 101.325 * 1e-3  # 1 atm [kPa]

        inputs['T_water'] = inputs['T_atm']  # same as atmospheric [K]
        inputs['p_water'] = inputs['p_atm']  # same as atmospheric [MPa]

        # methane, from https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html, Accessed 5/12/20
        inputs['fuel_HHV'] = 15.4  # [kWh/kg fuel]
        inputs['fuel_CO2'] = 2.75  # [kg CO2/kg fuel]

        # mechanical and generator losses
        inputs['loss_mech'] = 1.0 - 0.95  # [-]
        inputs['loss_gen'] = 1.0 - 0.975  # [-]

        # wellbore
        inputs['r_w'] = 0.41 / 2.0  # wellbore radius [m]
        inputs['epsilon'] = 0.002 * 1e-3  # pipe roughness [m]
        inputs['depth'] = 1402.35  # depth [m]

        # aquifer pressure gradient and limits
        inputs['p_hydro_grad'] = 10.0  # hydrostatic pressure gradient [MPa/km], Fukai et al. 2020
        inputs['p_frac_grad'] = 14.73  # fracture pressure gradient [MPa/km], Fukai et al. 2020
        inputs['safety_factor'] = 0.5  # operating pressure safety factor [-], Allen et al. 1983

        # aquifer thermal gradient
        inputs['T_grad_m'] = 0.007376668 * 3.28084  # m, slope [deg C/m], Battelle 2019
        inputs['T_grad_b'] = 7.412436  # b, intercept [deg C], Battelle 2019

        # storage geomechanical properties
        inputs['r_f'] = 117.0645423  # formation radius [m] (Default: 2000 MWh)
        inputs['h'] = 62.44  # thickness [m]
        inputs['phi'] = 0.2292  # porosity [-]
        inputs['Slr'] = 0.0  # liquid residual fraction [-]
        inputs['k'] = 38.67  # permeability [mD] #

        # aquifer mass losses
        inputs['loss_m_air'] = 3.5 / 100.0  # fraction of air lost in aquifer [-] #

        # operational conditions
        inputs['m_dot'] = 574.3625466  # mass flow rate [kg/s] (Default 200 MW)

        # operational constraint
        inputs['mach_limit'] = 0.3  # limited to this mach number

        return inputs

    def __init__(self, inputs=get_default_inputs()):

        # debug option
        self.debug = inputs['debug']  # debug
        self.buffer = 1e-6  # to prevent warnings when limits are exceeded due to numerical rounding

        # number of timesteps to use in single cycle simulations
        self.steps = inputs['steps']  # (-)

        # options to include/exclude various loss mechanisms
        self.include_air_leakage = inputs['include_air_leakage']
        self.include_aquifer_dp = inputs['include_aquifer_dp']
        self.include_thermal_gradient = inputs['include_thermal_gradient']
        self.include_pipe_dp_gravity = inputs['include_pipe_dp_gravity']
        self.include_pipe_dp_friction = inputs['include_pipe_dp_friction']
        self.include_pipe_heat_transfer = inputs['include_pipe_heat_transfer']

        # constants
        self.g = 9.81  # gravitational constant [m/s^2]
        self.R = 8.314  # universal gas constant [kJ/kmol-K]
        self.speed_of_sound = 343.0  # speed of sound in air [m/s]

        # atmospheric air properties
        self.air = "Air"  # CoolProp fluid name [-]
        self.M = 28.97  # molecular weight [kg/kmol]
        self.T_atm = inputs['T_atm'] + 273.15  # K
        self.p_atm = inputs['p_atm']  # [MPa]

        # water properties (used for cooling)
        self.water = 'Water'  # CoolProp fluid name [-]
        self.T_water = inputs['T_water'] + 273.15  # [K]
        self.p_water = inputs['p_water']  # [MPa]
        self.c_water = CP.PropsSI('CPMASS', 'T', self.T_water, 'P', self.p_water * 1e6,
                                  self.water) / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.v_water = 1.0 / CP.PropsSI('D', 'T', self.T_water, 'P', self.p_water * 1e6,
                                        self.water)  # specific volume (1/density) [m^3/kg]

        # fuel properties (default values are for natural gas)
        self.fuel_HHV = inputs['fuel_HHV']  # [kWh/kg]
        self.fuel_CO2 = inputs['fuel_CO2']  # [kg CO2/kg fuel]

        # efficiencies
        self.eta_mech = 1.0 - inputs['loss_mech']  # mechanical [fr]
        self.eta_gen = 1.0 - inputs['loss_gen']  # generator [fr]

        # wellbore
        self.r_w = inputs['r_w']  # wellbore radius [m]
        self.epsilon = inputs['epsilon']  # pipe roughness [m]
        self.depth = inputs['depth']  # depth [m]

        # aquifer pressure gradient and limits
        self.p_hydro_grad = inputs['p_hydro_grad']  # hydrostatic pressure gradient [MPa/km]
        self.p_frac_grad = inputs['p_frac_grad']  # fracture gradient [MPa/km]
        self.safety_factor = inputs['safety_factor']  # pressure safety factor [-]

        # calculated aquifer operating pressure range
        self.p_store_min = inputs['p_hydro_grad'] * inputs['depth'] * 1e-3  # minimum storage pressure[MPa]
        self.p_store_range = inputs['safety_factor'] * (
                inputs['p_frac_grad'] - inputs['p_hydro_grad']) * inputs['depth'] * 1e-3  # storage pressure range [MPa]
        self.p_store_max = self.p_store_min + self.p_store_range  # maximum storage pressure [MPa]
        self.p_store_max_actual = self.p_store_max  # actual depends on mass flow rate [MPa]

        # aquifer thermal gradient
        if self.include_thermal_gradient:
            self.T_grad_m = inputs['T_grad_m']  # m, slope [deg C/m]
            self.T_grad_b = inputs['T_grad_b']  # b, intercept [deg C]
        else:
            self.T_grad_m = 0.0
            self.T_grad_b = self.T_atm

        # calculated aquifer temperature
        self.T_store_init = 273.15 + self.T_grad_m * inputs['depth'] + self.T_grad_b  # storage temperature [K]

        # storage geomechanical properties
        if inputs['r_f'] > inputs['r_w']:
            self.r_f = inputs['r_f']  # radius [m]
        else:
            print('Warning: r_f must by => than r_w, r_f set to r_w')
            self.r_f = inputs['r_w']  # radius [m]
        self.h = inputs['h']  # thickness [m]
        self.phi = inputs['phi']  # porosity [-]
        self.Slr = inputs['Slr']  # residual liquid fraction [-]
        self.k = inputs['k']  # permeability [mD]

        # aquifer mass losses
        if self.include_air_leakage:
            self.loss_m_air = inputs['loss_m_air']  # fraction of air lost in aquifer [-] #
        else:
            self.loss_m_air = 0.0

        # operational
        self.m_dot = inputs['m_dot']

        # calculated storage volume and mass storage
        self.V_res = self.h * pi * self.r_f ** 2  # storage total volume [m^3]
        self.V = self.V_res * self.phi * (1.0 - self.Slr)  # volume available for air storage [m^3]
        self.m_store_min = self.p_store_min * 1e3 * self.V * self.M / (self.R * self.T_store_init)  # minimum [kg]
        self.m_store_max = self.p_store_max * 1e3 * self.V * self.M / (self.R * self.T_store_init)  # maximum [kg]
        self.m_store_max_actual = self.m_store_max  # actual maximum varies based on mass flow rate

        # storage  - initialize state
        self.time = 0.0  # [hr]
        self.T_store = self.T_store_init  # storage temperature [K]
        self.p_store = self.p_store_min  # storage pressure [MPa]
        self.m_store = self.m_store_min  # mass stored [kg]

        # flow pressure drops
        self.dp_pipe_f = 0.0  # pipe friction [MPa]
        self.f = 0.0  # pipe friction factor [-]
        self.dp_pipe_g = 0.0  # pipe gravitational potential [MPa]
        self.dp_aquifer = 0.0  # aquifer pressure drop [MPa]

        # pressure states [MPa]
        self.p0 = self.p_atm  # ambient / compressor inlet / expander outlet
        self.p1 = self.p_store  # compressor outlet / expander inlet
        self.p2 = self.p_store  # downwell
        self.p3 = self.p_store  # aquifer

        # temperature states [K]
        self.T0 = self.T_atm  # compressor inlet / expander outlet
        self.T1 = self.T_atm  # compressor outlet / expander inlet
        self.T2 = self.T_store  # downwell
        self.T3 = self.T_store  # aquifer

        # initialize at design flow rate to calculate machine design outlet pressure
        self.calc_pipe_dp(inputs['m_dot'])  # pipe friction and gravitational potential
        self.calc_aquifer_dp(inputs['m_dot'])  # aquifer pressure losses
        self.p_machine_design = self.p_store_max + self.dp_pipe_f + self.dp_pipe_g + self.dp_aquifer
        self.p_well_design_min = self.p_store_min + self.dp_pipe_g

        # store error messages for current state
        self.error_msg = ''

        # check if flow rate exceeds 0.1 mach limit
        self.mach_limit = inputs['mach_limit']
        rho = CP.PropsSI('D', 'T', self.T0, 'P', self.p_well_design_min * 1e6, self.air)  # density [kg/m3]
        U_max = self.speed_of_sound * inputs['mach_limit']  # max velocity [m/s]
        self.m_dot_max = rho * U_max * pi * self.r_w ** 2.0  # max flow rate [kg/s]
        if inputs['m_dot'] > self.m_dot_max:
            self.error_msg = 'Exceeds Mach limit'
            print('exceeded')
        if self.debug:
            print("p_well_design_min MPa   :" + str(self.p_well_design_min))
            print("rho               kg/m3 :" + str(rho))
            print("U_max             m/s   : " + str(U_max))
            print("m_dot_max         kg/s  : " + str(self.m_dot_max))

        # dataframe to store data
        self.attributes_time_series = ['time', 'm_dot', 'delta_t', 'm_air', 'm_air_leakage',
                                       'pwr', 'energy_in', 'energy_out',
                                       'work_per_kg', 'total_work_per_kg', 'water_per_kg',
                                       'fuel_per_kg',
                                       'm_water', 'm_fuel',
                                       'p_store', 'T_store', 'm_store',
                                       'p0', 'p1', 'p2', 'p3',
                                       'T0', 'T1', 'T2', 'T3',
                                       'dp_pipe_f', 'dp_pipe_g', 'dp_well',
                                       'error_msg']
        self.data = pd.DataFrame(columns=self.attributes_time_series)

    def update(self, m_dot=50.0, delta_t=1.0):
        """

        Updates the CAES system for the addition time step given a power request

        Designed to be kept the same for each caes architecture

        :param m_dot: mass flow rate, injection (+) or release (-) [kg/s]
        :param delta_t: time step [hr]
        :return:
        """

        # create series to hold results from this time step
        s = pd.Series(data=0.0, index=self.attributes_time_series)
        s['m_dot'] = m_dot
        s['delta_t'] = delta_t
        s['m_air'] = m_dot * 3600 * delta_t  # mass injection/release [kg]
        s['error_msg'] = self.error_msg

        # update time
        self.time = self.time + delta_t  # [hr]
        s['time'] = self.time

        # update flow pressure losses
        if abs(s['m_dot']) > 0:
            self.calc_pipe_dp(m_dot)  # pipe friction and gravitational potential
            self.calc_aquifer_dp(m_dot)  # aquifer pressure losses

            s['dp_pipe_f'] = self.dp_pipe_f
            s['dp_pipe_g'] = self.dp_pipe_g
            s['dp_well'] = self.dp_aquifer

        # charge/discharge
        if s['m_air'] > 0.0:  # (charge)

            # aquifer mass leakage (leakage occurs after air has been injected and traveled into the aquifer)
            s['m_air_leakage'] = s['m_air'] * self.loss_m_air

            # pressure states
            s['p0'] = self.p_atm  # atmospheric pressure, compressor inlet
            s['p1'] = self.p_store + self.dp_aquifer + self.dp_pipe_f + self.dp_pipe_g  # compressor outlet, pipe inlet
            s['p2'] = self.p_store + self.dp_aquifer  # pipe outlet
            s['p3'] = self.p_store  # storage pressure

            # temperature states
            s['T0'] = self.T_atm  # atmospheric pressure, compressor inlet
            s['T1'] = self.T_atm  # compressor outlet, pipe inlet # not updated
            s['T2'] = self.T_store  # pipe outlet # not updated
            s['T3'] = self.T_store  # storage pressure

            # calculate compressor performance
            s = self.charge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] / self.eta_mech / self.eta_gen

        elif s['m_air'] < 0.0:  # (discharge)

            # aquifer mass leakage  - does no occur during discharge
            s['m_air_leakage'] = 0.0

            # pressure states
            s['p3'] = self.p_store  # aquifer pressure
            s['p2'] = self.p_store - self.dp_aquifer  # pipe intlet
            s['p1'] = self.p_store - self.dp_aquifer - self.dp_pipe_f - self.dp_pipe_g  # pipe outlet, expander inlet
            s['p0'] = self.p_atm  # atmospheric pressure, expander outlet

            # temperature states
            s['T3'] = self.T_store  # aquifer
            s['T2'] = self.T_store  # pipe inlet
            s['T1'] = self.T_atm  # pipe outlet, expander inlet # not updated
            s['T0'] = self.T_atm  # expander outlet # not updated

            # calculate expander performance
            s = self.discharge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] * self.eta_mech * self.eta_gen

        else:  # no flow
            # pressure states
            s['p0'] = self.p_atm
            s['p1'] = self.p_store
            s['p2'] = self.p_store
            s['p3'] = self.p_store

            # temperature states [K]
            s['T0'] = self.T_atm  # compressor inlet / expander outlet
            s['T1'] = self.T_atm  # compressor outlet / expander inlet
            s['T2'] = self.T_store  # downwell
            s['T3'] = self.T_store  # aquifer

        # store pressure  and temperature states
        self.p0 = s['p0']
        self.p1 = s['p1']
        self.p2 = s['p2']
        self.p3 = s['p3']

        self.T0 = s['T0']
        self.T1 = s['T1']
        self.T2 = s['T2']
        self.T3 = s['T3']

        # calculate the power per time step
        s['pwr'] = -1.0 * s['m_air'] * s['total_work_per_kg'] / (3600 * delta_t)  # 3600 converts from hr to s

        # calculate water and fuel use
        s['m_water'] = s['water_per_kg'] * abs(s['m_air'])
        s['m_fuel'] = s['fuel_per_kg'] * abs(s['m_air'])

        # calculate energy in/out
        if s['m_air'] > 0.0:  # (charge)
            s['energy_in'] = -1.0 * s['m_air'] * s['total_work_per_kg'] / 3600  # [kWh]
        elif s['m_air'] < 0.0:  # (discharge)
            s['energy_out'] = -1.0 * s['m_air'] * s['total_work_per_kg'] / 3600  # [kWh]

        # update storage pressure
        s = self.update_storage_pressure(s)

        # -----------------------
        # finish storing results from current time step
        # -----------------------
        self.data = self.data.append(s, ignore_index=True)

        # clear warning messages for subsequent time step
        self.error_msg = ''

    def single_cycle(self):
        """
        runs a single cycle, charging and discharge in the number of steps specified in self.steps
        :param:
        m_dot [kg/s]
        :return:
        """

        # calculate aquifer pressure loss based on m_dot
        self.calc_aquifer_dp(self.m_dot)  # aquifer pressure losses

        # update m_store_max_actual based on aquifer pressure losses
        self.p_store_max_actual = self.p_store_max - self.dp_aquifer
        self.m_store_max_actual = self.p_store_max_actual * 1e3 * self.V * self.M / (
                self.R * self.T_store_init)  # maximum [kg]

        # mass injection/release per timestep (mass leakage compensated for during injection)
        m_air_in = (self.m_store_max_actual - self.m_store_min) / self.steps / (1 - self.loss_m_air)
        m_air_out = (self.m_store_max_actual - self.m_store_min) / self.steps

        # timestep duration
        delta_t_in = m_air_in / (self.m_dot * 3600)  # [hr]
        delta_t_out = m_air_out / (self.m_dot * 3600)  # [hr]

        if self.debug:
            print('mdot        [kg/s] : ' + str(round(self.m_dot, 2)))
            print('m_air_in    [kg]   : ' + str(round(m_air_in, 2)))
            print('m_air_out   [kg]   : ' + str(round(m_air_out, 2)))
            print('delta_t_in  [hr]   : ' + str(round(delta_t_in, 2)))
            print('delta_t_out [hr]   : ' + str(round(delta_t_out, 2)))

        # save initial state
        self.update(m_dot=0.0, delta_t=1e-6)

        # if aquifer pressure losses are greater than well range, then do not perform calculations
        if m_air_in > 0.0:

            # ========================
            # charging
            # ========================

            if self.debug:
                print("Charging")

            for i in range(int(self.steps)):
                # charge
                self.update(m_dot=self.m_dot, delta_t=delta_t_in)
                if self.debug:
                    print('/t' + str(i) + ' of ' + str(self.steps))

            # ========================
            # discharging
            # ========================
            if self.debug:
                print("Discharging")

            for i in range(int(self.steps)):
                # discharge
                self.update(m_dot=-1.0 * self.m_dot, delta_t=delta_t_out)
                if self.debug:
                    print('/t' + str(i) + ' of ' + str(self.steps))

    def debug_perf(self, delta_t=1.0):
        """
        runs several charge and discharge steps to debug calculations
        :param delta_t: time step [hr]
        :return:
        """
        m_dot_in = 1.0 * self.m_dot
        m_dot_out = -1.0 * self.m_dot

        n_steps = 5

        # charge
        for i in range(n_steps):
            self.update(m_dot=m_dot_in, delta_t=delta_t)
        # discharge
        for i in range(n_steps):
            self.update(m_dot=m_dot_out, delta_t=delta_t)

    def analyze_performance(self):
        """

        analyzes system performance - meant to be performed after completing a full cycle of charging/discharging

        designed to be kept the same for each caes architecutre

        :return: results - Pandas Series with the following entries
            RTE - roud trip efficiency [fr]
            fuel_per_MWh - fuel consumption oer MWh [kg]
            CO2_per_MWh - CO2 emissions per MWh [kg]
            water_per_MWh - water consumption per MWh [kg]
        """
        # create series to hold results
        entries = ['RTE', 'kWh_in', 'kWh_out', 'kW_in_avg', 'kW_out_avg',
                   'kg_water_per_kWh', 'kg_CO2_per_kWh', 'kg_fuel_per_kWh',
                   'dp_well_avg', 'dp_pipe_f_avg', 'errors']
        results = pd.Series(index=entries)

        if len(self.data) > 1:

            # compute performance
            energy_input_total = self.data.loc[:, 'energy_in'].sum()  # [kWh]
            energy_output_total = self.data.loc[:, 'energy_out'].sum()  # [kWh]
            water_input_total = self.data.loc[:, 'm_water'].sum()  # [kg]
            fuel_input_total = self.data.loc[:, 'm_fuel'].sum()  # [kg]
            CO2_fuel = fuel_input_total * self.fuel_CO2  # [ton]
            heat_input_total = fuel_input_total * self.fuel_HHV  # [kWh]
            RTE = energy_output_total / (energy_input_total + heat_input_total)

            # power in/out indices
            ind_pwr_in = self.data.loc[:, 'm_air'] > 0.0
            ind_pwr_out = self.data.loc[:, 'm_air'] < 0.0
            ind_pwr = self.data.loc[:, 'm_air'] != 0.0

            # store results
            results['RTE'] = RTE
            results['kWh_in'] = energy_input_total
            results['kWh_out'] = energy_output_total
            results['kW_in_avg'] = self.data.loc[ind_pwr_in, 'pwr'].mean()
            results['kW_out_avg'] = self.data.loc[ind_pwr_out, 'pwr'].mean()
            results['kg_water_per_kWh'] = water_input_total / energy_output_total
            results['kg_CO2_per_kWh'] = CO2_fuel / energy_output_total
            results['kg_fuel_per_kWh'] = fuel_input_total / energy_output_total
            results['MWh_cushion_gas'] = self.m_store_min / self.m_dot / 3600 * results['kW_in_avg'] / 1000.0
            results['dp_well_avg'] = self.data.loc[ind_pwr, 'dp_well'].mean()
            results['dp_pipe_f_avg'] = self.data.loc[ind_pwr, 'dp_pipe_f'].mean()

            # check for errors
            if len(self.data.error_msg.unique()) > 1:  # errors
                results['errors'] = 'true'
            elif energy_input_total == 0 or energy_output_total == 0 or RTE <= 0:
                results['errors'] = 'true'
            else:  # no errors
                results['errors'] = 'false'

        else:  # insufficient data
            results['errors'] = 'true'

        return results

    def update_storage_pressure(self, s):
        """

        updates the pressure of the storage based on mass added/removed with machinery

        designed to be kept the same for each caes architecutre

        :param:
            s - pandas series containing performance of current time step and error messages
        :return:
            s - updated
        """
        # update storage mass and pressure
        self.m_store = self.m_store + s['m_air'] - s['m_air_leakage']
        self.p_store = self.m_store * self.R * self.T_store / (self.V * self.M) * 1e-3  # storage pressure

        # check storage pressure against limits, p2 (downwell)
        if self.p2 > self.p_store_max + self.buffer:
            s['error_msg'] = 'Error: p2 > P_store_max (' + str(self.p2) + ' > ' + str(self.p_store_max) + ')'
            print(s['error_msg'])

        # check storage pressure against limits, p3 (formation edge)
        if self.p3 < self.p_store_min - self.buffer:
            s['error_msg'] = 'Error: p3 < P_store_min (' + str(self.p3) + ' < ' + str(self.p_store_min) + ')'
            print(s['error_msg'])
        elif self.p3 > self.p_store_max + self.buffer:
            s['error_msg'] = 'Error: p3 > P_store_max (' + str(self.p3) + ' > ' + str(self.p_store_max) + ')'
            print(s['error_msg'])

        # store results
        s['p_store'] = self.p_store
        s['T_store'] = self.T_store
        s['m_store'] = self.m_store

        return s

    def charge_perf(self, s):
        """

        charge_perf - performance of compressors to store energy

        designed to be updated for each caes architecture

        :param:
            s - pandas series containing performance of current time step and error messages
        :return:
            s - updated including (at a minimum) the following entries:
                work_per_kg - compression work [kJ/kg air]
                water_per_kg - water use [kg water /kg air ]
                fuel_per_kg - fuel use [kg fuel /kg air]
        """

        # idealized isothermal process
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(s['p0'] / s['p1'])  # [kJ/kg]
        s['water_per_kg'] = 0.0  # idealized process - no cooling water [kg/kg air]
        s['fuel_per_kg'] = 0.0  # isothermal - no heat input [kg/kg air]

        return s

    def discharge_perf(self, s):
        """
        discharge_perf - performance of expanders to release energy from storage

        designed to be updated for each caes architecture

        :param:
            s - pandas series containing performance of current time step and error messages
        :return:
            s - updated including (at a minimum) the following entries:
                work_per_kg - compression work [kJ/kg air]
                water_per_kg - water use [kg water /kg air ]
                fuel_per_kg - fuel use [kg fuel /kg air]
        """

        # idealized isothermal process
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(s['p1'] / s['p0'])  # [kJ/kg]
        s['water_per_kg'] = 0.0  # idealized process - no cooling water [kg/kg air]
        s['fuel_per_kg'] = 0.0  # isothermal - no heat input [kg/kg air]

        return s

    def calc_aquifer_dp(self, m_dot):
        if self.include_aquifer_dp:
            # fluid properties, inputs are degrees K and Pa
            rho = CP.PropsSI('D', 'T', self.T_store, 'P', self.p_store * 1e6, self.air)  # density, [kg/m3]
            mu = CP.PropsSI('V', 'T', self.T_store, 'P', self.p_store * 1e6,
                            self.air) * 1000  # Viscosity, convert Pa*s (output) to cP
            Z = CP.PropsSI('Z', 'T', self.T_store, 'P', self.p_store * 1e6, self.air)  # gas deviation factor [-]

            Q = m_dot / rho  # radial flow rate [m3/s]

            # aquifer pressure drop function
            dp = aquifer_dp(Q=Q, r_f=self.r_f, r_w=self.r_w, k=self.k, mu=mu, h=self.h, p_f=self.p_store,
                            T=self.T_store,
                            Z=Z)  # [MPa]

            self.dp_aquifer = abs(dp)  # [MPa]
        else:
            self.dp_aquifer = 0.0  # [MPa]

    def calc_pipe_dp(self, m_dot):
        # determine thermodynamic state to use
        if m_dot > 0.0:  # injection
            T = self.T1
            p = self.p1
        else:  # withdrawl / no movement
            T = self.T2
            p = self.p2

        # fluid properties, inputs are degrees K and Pa
        rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, self.air)  # density [kg/m3]
        mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, self.air)  # viscosity [Pa*s]

        # pipe diameter
        d = 2 * self.r_w

        # friction
        if self.include_pipe_dp_friction:
            self.dp_pipe_f, self.f = pipe_fric_dp(epsilon=self.epsilon, d=d, depth=self.depth, m_dot=m_dot, rho=rho,
                                                  mu=mu)  # [MPa]
        else:
            self.dp_pipe_f = 0.0
            self.f = 0.0

        # gravity
        if self.include_pipe_dp_gravity:
            self.dp_pipe_g = pipe_grav_dp(m_dot=m_dot, rho=rho, z=self.depth)  # [MPa]
        else:
            self.dp_pipe_g = 0.0

    def plot_overview(self, casename=''):
        df = self.data
        df.loc[:, 'step'] = df.index

        x_var = 'time'
        x_label = 'Time [hr]'
        x_convert = 1.0

        y_vars = ['m_store', 'p_store', 'total_work_per_kg', 'pwr']
        y_labels = ['Air stored\n[kton]', 'Well pressure\n[MPa]', 'Work\n[kJ/kg]', 'Power\n[MW]']
        y_converts = [1.0e-6, 1.0, 1.0, 1.0e-3]

        plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts)
        plt.savefig(casename + 'overview.png', dpi=600)
        plt.close()

    def plot_pressures(self, casename=''):
        df = self.data
        df.loc[:, 'step'] = df.index

        x_var = 'time'
        x_label = 'Time [hr]'
        x_convert = 1.0

        y_vars = ['m_dot', 'p0', 'p1', 'p2', 'p3']
        y_labels = ['Mass flow\n[kg/s]', 'p0\nAmbient\n[MPa]', 'p1 \nWell top\n[MPa]',
                    'p2\nWell btm\n[MPa]', 'p3\nAquifer\n[MPa]']
        y_converts = [1.0, 1.0, 1.0, 1.0, 1.0]

        plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts)
        plt.savefig(casename + 'pressures.png', dpi=600)
        plt.close()

    def plot_pressure_losses(self, casename=''):
        df = self.data
        df.loc[:, 'step'] = df.index

        x_var = 'time'
        x_label = 'Time [hr]'
        x_convert = 1.0

        y_vars = ['m_dot', 'dp_pipe_f', 'dp_pipe_g', 'dp_well']
        y_labels = ['Mass flow\n[kg/s]',
                    'Pipe friction\n[MPa]', 'Gravitational loss\n[MPa]', 'Aquifer\n[MPa]']
        y_converts = [1.0, 1.0, 1.0, 1.0]

        plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts)
        plt.savefig(casename + 'pressure_losses.png', dpi=600)
        plt.close()
