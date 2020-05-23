import pandas as pd
import numpy as np
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import log


class CAES:

    def get_default_inputs():
        attributes = ['debug', 'steps', 'T_atm', 'p_atm', 'T_water', 'p_water', 'fuel_HHV', 'fuel_CO2', 'eta_mech',
                      'eta_storage',
                      'T_store_init', 'p_store_init', 'V_res', 'phi', 'Slr']
        inputs = pd.Series(index=attributes)

        inputs['debug'] = False  # debug
        inputs['steps'] = 100.0  # number of timesteps to use in single cycle simulation

        inputs['T_atm'] = 298.15  # 25 deg C [K]
        inputs['p_atm'] = 101.325  # 1 atm [kPa]

        inputs['T_water'] = 298.15  # 25 deg C [K]
        inputs['p_water'] = 101.325  # 1 atm [kPa]

        # methane, from https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html, Accessed 5/12/20
        inputs['fuel_HHV'] = 15.4  # [kWh/kg fuel]
        inputs['fuel_CO2'] = 2.75  # [kg CO2/kg fuel]

        inputs['eta_mech'] = 0.95  # [-]
        inputs['eta_gen'] = 0.975  # [-]
        inputs['eta_storage'] = 0.985  # [-]

        inputs['T_store_init'] = 298.15  # 25 deg C [K]
        inputs['p_store_init'] = 10.0e3  # [kPa]
        inputs['p_store_min'] = 10.0e3  # [kPa]
        inputs['p_store_max'] = 22.0e3  # [kPa]

        inputs['V_res'] = 5.88e4  # [m3]
        inputs['phi'] = 0.29  # porosity [-]
        inputs['Slr'] = 0.0  # liquid residual fraction [-]

        return inputs

    def __init__(self, inputs=get_default_inputs()):

        # debug option
        self.debug = inputs['debug']  # debug
        self.buffer = 1e-6  # to prevent warnings when limits are exceeded due to numerical rounding

        # number of timesteps to use in single cycle simulations
        self.steps = inputs['steps']  # (-)

        # constants
        self.g = 9.81  # gravitational constant [m/s^2]
        self.R = 8.314  # universal gas constant [kJ/kmol-K]

        # atmospheric air properties
        self.air = "Air.mix"  # CoolProp fluid name [-]
        self.M = 28.97  # molecular weight [kg/kmol]
        self.T_atm = inputs['T_atm']  # K
        self.p_atm = inputs['p_atm']  # [kPa]

        # water properties (used for cooling)
        self.water = 'Water'  # CoolProp fluid name [-]
        self.T_water = inputs['T_water']  # [K]
        self.p_water = inputs['p_water']  # [kPa]
        self.c_water = CP.PropsSI('CPMASS', 'T', self.T_water, 'P', self.p_water * 1000.0,
                                  self.water) / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.v_water = 1.0 / CP.PropsSI('D', 'T', self.T_water, 'P', self.p_water * 1000.0,
                                        self.water)  # specific volume (1/density) [m^3/kg]

        # fuel properties (default values are for natural gas)
        self.fuel_HHV = inputs['fuel_HHV']  # [kWh/kg]
        self.fuel_CO2 = inputs['fuel_CO2']  # [kg CO2/kg fuel]

        # efficiencies
        self.eta_mech = inputs['eta_mech']  # mechanical [fr]
        self.eta_gen = inputs['eta_gen']  # generator [fr]
        self.eta_storage = inputs['eta_storage']  # storage round-trip-efficiency [fr]

        # storage properties
        self.p_store_min = inputs['p_store_min']  # [kPa]
        self.p_store_max = inputs['p_store_max']  # [kPa]
        self.V_res = inputs['V_res']  # storage total volume [m^3], formation total size or cavern volume
        self.phi = inputs['phi']  # porosity [-], set to 1.0 for cavern
        self.Slr = inputs['Slr']  # residual liquid fraction [-], set to 0.0 for cavern
        self.V = self.V_res * self.phi * (1.0 - self.Slr)  # volume available for air storage

        # storage  - initialize state
        self.T_store = inputs['T_store_init']  # storage temperature [K]
        if inputs['p_store_init'] < inputs['p_store_min']:
            inputs['p_store_init'] = inputs['p_store_min']
        self.p_store = inputs['p_store_init']  # storage pressure [MPa]
        self.m_store = self.p_store * self.V * self.M / (self.R * self.T_store)  # mass stored
        self.m_store_min = self.p_store_min * self.V * self.M / (self.R * self.T_store)  # mass stored
        self.m_store_max = self.p_store_max * self.V * self.M / (self.R * self.T_store)  # mass stored

        # store error messages for current state
        self.error_msg = ''

        # dataframe to store data
        self.attributes_time_series = ['time', 'delta_t', 'pwr', 'energy_in', 'energy_out',
                                       'work_per_kg', 'total_work_per_kg', 'water_per_kg',
                                       'fuel_per_kg',
                                       'm_air', 'm_water', 'm_fuel',
                                       'p_store', 'T_store', 'm_store',
                                       'error_msg']
        self.data = pd.DataFrame(columns=self.attributes_time_series)

    def update(self, pwr, delta_t=1.0):
        """

        Updates the CAES system for one time step given a power request

        Designed to be kept the same for each caes architecutre

        :param delta_t: time step [hr]
        :param pwr: power input (-) or output (+) [kW]
        :return:
        """
        # clear warning messages from previous time step
        self.error_msg = ''

        # create series to hold results from this time step
        s = pd.Series(data=0.0, index=self.attributes_time_series)
        s['pwr'] = pwr
        s['delta_t'] = delta_t

        # Charge/discharge
        if pwr < 0.0:  # (charge)

            # calculate compressor performance
            s = self.charge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] / self.eta_mech / self.eta_gen / self.eta_storage ** 0.5

        elif pwr > 0.0:  # (discharge)

            # calculate expander performance
            s = self.discharge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] * self.eta_mech * self.eta_gen * self.eta_storage ** 0.5

        # calculate mass change per time step
        s['m_air'] = -1.0 * abs(pwr) * delta_t * 3600 / s['total_work_per_kg']  # 3600 converts from kWh to kJ

        # check if this will go above or below pressure limits, if so, enfore limits
        if self.m_store + s['m_air'] > self.m_store_max:
            s['m_air'] = abs(self.m_store_max - self.m_store)
            s['pwr'] = -1.0 * abs(s['total_work_per_kg'] * s['m_air'] / (delta_t * 3600))
        elif self.m_store + s['m_air'] < self.m_store_min:
            s['m_air'] = -1.0 * abs(self.m_store - self.m_store_min)
            s['pwr'] = abs(s['total_work_per_kg'] * s['m_air'] / (delta_t * 3600))

        s['m_water'] = s['water_per_kg'] * abs(s['m_air'])
        s['m_fuel'] = s['fuel_per_kg'] * abs(s['m_air'])

        if pwr < 0.0:  # (charge)
            s['energy_in'] = abs(pwr) * delta_t  # [kWh]
        elif pwr > 0.0:  # (discharge)
            s['energy_out'] = abs(pwr) * delta_t  # [kWh]

        # update storage pressure
        s = self.update_storage_pressure(s)

        # -----------------------
        # finish storing results from current time step
        # -----------------------
        self.data = self.data.append(s, ignore_index=True)

    def update_mass(self, m_air, delta_t=1.0):
        """

        Updates the CAES system for the addition time step given a power request

        Designed to be kept the same for each caes architecutre

        :param delta_t: time step [hr]
        :param m_air: mass injection (+) or release (-) [kg]
        :return:
        """
        # clear warning messages from previous time step
        self.error_msg = ''

        # create series to hold results from this time step
        s = pd.Series(data=0.0, index=self.attributes_time_series)
        s['m_air'] = m_air
        s['delta_t'] = delta_t

        # check if this will go above or below pressure limits, if so, enfore limits
        if self.m_store + s['m_air'] > self.m_store_max:
            s['m_air'] = abs(self.m_store_max - self.m_store)
        elif self.m_store + s['m_air'] < self.m_store_min:
            s['m_air'] = -1.0 * abs(self.m_store - self.m_store_min)

        # Charge/discharge
        if s['m_air'] > 0.0:  # (charge)

            # calculate compressor performance
            s = self.charge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] / self.eta_mech / self.eta_gen / self.eta_storage ** 0.5

        elif s['m_air'] < 0.0:  # (discharge)

            # calculate expander performance
            s = self.discharge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] * self.eta_mech * self.eta_gen * self.eta_storage ** 0.5

        # calculate the power per time step
        s['pwr'] = -1.0 * s['m_air'] * s['total_work_per_kg'] / (3600 * delta_t)  # 3600 converts from hr to s

        # calculate water and fuel use
        s['m_water'] = s['water_per_kg'] * abs(s['m_air'])
        s['m_fuel'] = s['fuel_per_kg'] * abs(s['m_air'])

        # calculate energy stored
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

    def single_cycle(self):
        """
        runs a single cycle, charging and discharge in the number of steps specified in self.steps
        :param:
        :return:
        """

        # mass injection per timestep
        m_air = (self.m_store_max - self.m_store_min) / self.steps
        # nondimensional time, start at 0, full at 0.5, empty at 1.0
        delta_t = 1.0 / (self.steps * 2.0)

        # save initial state
        self.update_mass(m_air=0.0, delta_t=1e-6)

        if self.debug:
            print("Charging")

        for i in range(int(self.steps)):
            # charge
            self.update_mass(m_air, delta_t=delta_t)
            if self.debug:
                print('/t' + str(i) + ' of ' + str(self.steps))

        if self.debug:
            print("Discharging")

        for i in range(int(self.steps)):
            # discharge
            self.update_mass(-1.0 * m_air, delta_t=delta_t)
            if self.debug:
                print('/t' + str(i) + ' of ' + str(self.steps))

    def debug(self, pwr):
        """
        runs several charge and discharge steps to debug calculations
        :param pwr:
        :return:
        """
        pwr_in = -1.0 * pwr
        pwr_out = 1.0 * pwr

        # charge
        self.update(pwr_in)
        self.update(pwr_in)
        self.update(pwr_in)
        self.update(pwr_in)
        self.update(pwr_in)
        # discharge
        self.update(pwr_out)
        self.update(pwr_out)
        self.update(pwr_out)
        self.update(pwr_out)
        self.update(pwr_out)

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

        # compute performance
        energy_input_total = self.data.loc[:, 'energy_in'].sum()  # [kWh]
        energy_output_total = self.data.loc[:, 'energy_out'].sum()  # [kWh]
        water_input_total = self.data.loc[:, 'm_water'].sum()  # [kg]
        fuel_input_total = self.data.loc[:, 'm_fuel'].sum()  # [kg]
        CO2_fuel = fuel_input_total * self.fuel_CO2  # [ton]
        heat_input_total = fuel_input_total * self.fuel_HHV  # [kWh]
        RTE = energy_output_total / (energy_input_total + heat_input_total)

        # create series to hold results
        entries = ['RTE', 'kWh_in', 'kWh_out',
                   'kg_water_per_kWh', 'kg_CO2_per_kWh', 'kg_fuel_per_kWh', ]
        results = pd.Series(index=entries)
        results['RTE'] = RTE
        results['kWh_in'] = energy_input_total
        results['kWh_out'] = energy_output_total
        results['kg_water_per_kWh'] = water_input_total / energy_output_total
        results['kg_CO2_per_kWh'] = CO2_fuel / energy_output_total
        results['kg_fuel_per_kWh'] = fuel_input_total / energy_output_total

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
        self.m_store = self.m_store + s['m_air']
        self.p_store = self.m_store * self.R * self.T_store / (self.V * self.M)  # storage pressure

        # check storage pressure against limits
        if self.p_store < self.p_store_min - self.buffer:
            s['error_msg'] = 'Error: P_store < P_store_min (' + str(self.p_store) + ' < ' + str(self.p_store_min) + ')'
            print(s['error_msg'])
        elif self.p_store > self.p_store_max + self.buffer:
            s['error_msg'] = 'Error: P_store > P_store_max (' + str(self.p_store) + ' > ' + str(self.p_store_max) + ')'
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
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(self.p_atm / self.p_store)  # [kJ/kg]
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
        s['work_per_kg'] = self.R / self.M * self.T_atm * log(self.p_store / self.p_atm)  # [kJ/kg]
        s['water_per_kg'] = 0.0  # idealized process - no cooling water [kg/kg air]
        s['fuel_per_kg'] = 0.0  # isothermal - no heat input [kg/kg air]

        return s
