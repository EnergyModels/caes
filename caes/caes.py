import pandas as pd
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function
from math import log


class CAES:

    def __init__(self, delta_t=0.08333,  # 5 min
                 T_atm=298.15, p_atm=101.325,
                 T_water=298.15, p_water=101.325,
                 fuel_HHV=15.4, fuel_CO2=2.75,
                 eta_mech=0.95, eta_gen=0.975, eta_storage=0.985,
                 T_store_init=298.15, P_store_init=1.0e3, P_store_min=1.0e3, P_store_max=10.0e3,
                 V_res=5e3, phi=0.15, Slr=0.8):

        # time step
        self.delta_t = delta_t  # [hr]

        # constants
        self.g = 9.81  # gravitational constant [m/s^2]
        self.R = 8.314  # universal gas constant [kJ/kmol-K]

        # atmospheric air properties
        self.air = "Air.mix"  # CoolProp fluid name [-]
        self.M = 28.97  # molecular weight [kg/kmol]
        self.T_atm = T_atm  # K
        self.p_atm = p_atm  # [kPa]

        # water properties (used for cooling)
        self.water = 'Water'  # CoolProp fluid name [-]
        self.T_water = T_water  # [K]
        self.p_water = p_water  # [kPa]
        self.c_water = CP.PropsSI('CPMASS', 'T', self.T_water, 'P', self.p_water*1000.0,
                                  self.water) / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.v_water = 1.0 / CP.PropsSI('D', 'T', self.T_water, 'P', self.p_water*1000.0,
                                      self.water)  # specific volume (1/density) [m^3/kg]

        # fuel properties (default values are for natural gas)
        self.fuel_HHV = fuel_HHV  # [kWh/kg] https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html Accessed 5/12/20
        self.fuel_CO2 = fuel_CO2  # [kg CO2/kg fuel]  https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html Accessed 5/12/20

        # efficiencies
        self.eta_mech = eta_mech  # mechanical [fr]
        self.eta_gen = eta_gen  # generator [fr]
        self.eta_storage = eta_storage  # storage round-trip-efficiency [fr]

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
        self.attributes_time_series = ['pwr', 'energy_in', 'energy_out',
                                       'work_per_kg', 'total_work_per_kg', 'water_per_kg',
                                       'fuel_per_kg',
                                       'm_air', 'm_water', 'm_fuel',
                                       'p_store', 'T_store', 'm_store',
                                       'error_msg']
        self.data = pd.DataFrame(columns=self.attributes_time_series)

    def update(self, pwr):
        """

        Updates the CAES system for one time step given a power request

        Designed to be kept the same for each caes architecutre

        :param pwr: power input (-) or output (+) [kW]
        :return:
        """
        # clear warning messages from previous time step
        self.error_msg = ''

        # create series to hold results from this time step
        s = pd.Series(data=0.0, index=self.attributes_time_series)
        s['pwr'] = pwr

        # Charge/discharge
        if pwr < 0.0:  # (charge)
            s['energy_in'] = abs(pwr) * self.delta_t  # [kWh]

            # calculate compressor performance
            s = self.charge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] / self.eta_mech / self.eta_gen / self.eta_storage ** 0.5

        elif pwr > 0.0:  # (discharge)
            s['energy_out'] = abs(pwr) * self.delta_t  # [kWh]

            # calculate expander performance
            s = self.discharge_perf(s)

            # apply mechanical, generator and storage efficienies
            s['total_work_per_kg'] = s['work_per_kg'] * self.eta_mech * self.eta_gen * self.eta_storage ** 0.5

        # calculate mass change per time step
        s['m_air'] = -1.0 * abs(pwr) * self.delta_t * 3600 / s['total_work_per_kg']  # 3600 converts from kWh to kJ
        s['m_water'] = s['water_per_kg'] * abs(s['m_air'])
        s['m_fuel'] = s['fuel_per_kg'] * abs(s['m_air'])

        # update storage pressure
        s = self.update_storage_pressure(s)

        # -----------------------
        # finish storing results from current time step
        # -----------------------
        self.data = self.data.append(s, ignore_index=True)

    def single_cycle(self, pwr):
        """
        runs a single cycle, charging and discharge at the rate pwr (kW)
        :param pwr:
        :return:
        """
        pwr_in = -1.0 * pwr
        pwr_out = 1.0 * pwr

        while self.p_store < self.p_store_max:
            self.update(pwr_in)
        while self.p_store > self.p_store_min:
            self.update(pwr_out)

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
        if self.p_store < self.p_store_min:
            s['error_msg'] = 'Error: P_store < P_store_min'
            print(s['error_msg'])
        elif self.p_store > self.p_store_max:
            s['error_msg'] = 'Error: P_store > P_store_max'
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
