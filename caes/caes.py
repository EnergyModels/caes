import pandas as pd
import numpy as np
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import log


class CAES:

    def __init__(self, delta_t=0.1,
                 T_atm=298.15, P_atm=101.325,
                 T_water=298.15, P_water=101.325,
                 fuel_HHV=1.0, fuel_CO2=1.0,  # TODO update
                 T_store_init=298.15, P_store_init=1.0, P_store_min=1.0, P_store_max=10.0,
                 V_res=1e3, phi=0.15, Slr=0.8):

        # time step
        self.delta_t = delta_t  # [hr]

        # constants
        self.g = 9.81  # gravitational constant [m/s^2]
        self.R = 8.314  # universal gas constant [kJ/kmol-K]

        # atmospheric air properties
        self.air = "Air.mix"  # CoolProp fluid name [-]
        self.M = 28.97  # molecular weight [kg/kmol]
        self.T_atm = T_atm  # K
        self.p_atm = P_atm  # [kPa]

        # water properties (used for cooling)
        self.water = 'Water'  # CoolProp fluid name [-]
        self.T_water = T_water  # [K]
        self.P_water = P_water  # [kPa]
        self.c_water = CP.PropsSI('CPMASS', 'T', self.T_water, 'P', self.p_water,
                                  self.water)  # constant pressure specific heat [J/kg-K]

        # fuel properties (default values are for natural gas)
        self.fuel_HHV = fuel_HHV
        self.fuel_CO2 = fuel_CO2

        # storage properties
        self.p_store_min = P_store_min  # [kPa]
        self.p_store_max = P_store_max  # [kPa]
        self.V_res = V_res  # storage total volume [m^3], formation total size or cavern volume
        self.phi = phi  # porosity [-], set to 1.0 for cavern
        self.Slr = Slr  # residual liquid fraction [-], set to 0.0 for cavern
        self.V = V_res * phi * (1.0 - Slr)  # volume available for air storage

        # storage  - initialize state
        self.T_store = T_store_init  # storage temperature [K]
        self.p_store = P_store_init  # storage pressure [MPa]
        self.m_store = self.p_store * self.V * self.M / (self.R * self.T_store)  # mass stored

        # store error messages for current state
        self.error_msg = ''

        # dataframe to store data
        self.attributes_time_series = ['pwr',
                                       'm_air', 'm_water', 'm_fuel',
                                       'P_store', 'T_store', 'm_store',
                                       'error_msg']
        self.data = pd.DataFrame(data=0.0, columns=self.attributes_time_series)

    def update(self, pwr):
        """

        Updates the CAES system for one time step given a power request

        Designed to be kept the same for each caes architecutre

        :param pwr: power input (-) or output (+)
        :return:
        """
        # clear warning messages from previous time step
        self.error_msg = ''

        # create series to hold results from current time step
        s = pd.Series(data=0.0, index=self.attributes_time_series)
        s['pwr'] = pwr

        # Charge/discharge
        if pwr < 0.0:  # (charge)
            s = self.charge(s)

        elif pwr > 0.0:  # (discharge)
            s = self.discharge(s)

        # update storage pressure
        self.update_storage_pressure(s)

        # -----------------------
        # save current state and any error messages
        # -----------------------
        s['P_store'] = self.P_store
        s['T_store'] = self.T_store
        s['m_store'] = self.m_store
        s['error_msg'] = self.error_msg
        self.data = self.data.append(s, ignore_index=True)

    def analyze_performance(self):
        """

        designed to be kept the same for each caes architecutre

        :return:
        """

        # compute performance
        pwr_input_total = 0.0  # TODO
        pwr_output_total = 0.0  # TODO
        water_input_total = 0.0  # TODO
        fuel_input_total = 0.0  # kg
        CO2_fuel = fuel_input_total * self.fuel_CO2  # ton
        heat_input_total = fuel_input_total * self.fuel_HHV  # TODO units
        RTE = pwr_output_total / (pwr_input_total + heat_input_total)

        # create series to hold results
        entries = ['RTE', 'CO2', 'fuel', 'water']
        results = pd.Series(index=entries)
        results['RTE'] = RTE
        results['fuel_per_MWh'] = fuel_input_total / pwr_output_total
        results['CO2_per_MWh'] = CO2_fuel / pwr_output_total
        results['water_per_MWh'] = water_input_total / pwr_output_total

        return results

    def update_storage_pressure(self, s):
        """

        designed to be kept the same for each caes architecutre

        :param s: Pandas Series that contains details of the current timestep
        :return:
        """
        # update storage mass and pressure
        self.m_store = self.m_store + s['m_air']
        self.p_store = self.m_store * self.R * self.T_store / (self.V * self.M)  # storage pressure

        # check storage pressure against limits
        if self.P_store < self.P_store_min:
            error_msg = 'Error: P_store < P_store_min'
            self.error_msg = self.msg + error_msg
            print(error_msg)
        if self.P_store > self.P_store_max:
            error_msg = 'Error: P_store > P_store_max'
            self.error_msg = self.msg + error_msg
            print(error_msg)

    def charge(self, s):
        """

        charge - charge storage with compressors to store energy

        designed to be updated for each caes architecture

        :param s: Pandas Series that contains details of the current timestep
        :return s: updated Pandas Series
        """

        # idealized isothermal process
        work_per_kg = self.R / self.M * self.T_atm * log(self.p_atm / self.p_store)

        # apply mechanical and storage efficienies
        total_work_per_kg = work_per_kg / self.eta_mech / self.eta_storage

        # calculate
        s['m_air'] = s['pwr'] / total_work_per_kg
        s['m_water'] = 0.0  # idealized process - no cooling water
        s['m_fuel'] = 0.0  # isothermal - no heat input
        return s

    def discharge(self, s):
        """
        discharge - discharge storage with expanders to release energy

        designed to be updated for each caes architecture

        :param s: Pandas Series that contains details of the current timestep
        :return s: updated Pandas Series
        """

        # idealized isothermal process
        work_per_kg = self.R / self.M * self.T_atm * log(self.p_store / self.p_atm)

        # apply mechanical efficiency (storage efficieny only applied to charge)
        total_work_per_kg = work_per_kg * self.eta_mech

        # calculate
        s['m_air'] = s['pwr'] / total_work_per_kg
        s['m_water'] = 0.0  # idealized process - no cooling water
        s['m_fuel'] = 0.0  # isothermal - no heat input
        return s
