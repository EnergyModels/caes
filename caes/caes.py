import pandas as pd
import numpy as np

attributes_time_series = ['pwr', 'pwr_curtail', 'heat',
                          'm_air', 'm_water', 'm_fuel',
                          'P_store', 'T_store']

class CAES:

    def __init__(self, delta_t=1.0,
                 T_store_init=298.15, P_store_init=1.0, P_store_min=1.0, P_store_max=10.0,
                 T_atm=298.15, P_atm=0.101325,
                 T_water=298.15, P_water=0.101325,
                 fuel_HHV=, fuel_CO2=):

        # time step
        self.delta_t = delta_t  # hr

        # storage
        self_T_store = T_store_init  # K
        self.P_store = P_store_init  # MPa
        self.P_store_min = P_store_min  # MPa
        self.P_store_max = P_store_max  # MPa

        # atmospheric conditions
        self.T_atm = T_atm  # K
        self.P_atm = P_atm  # MPa

        # water properties
        self.T_water = T_water  # K
        self.P_water = P_water  # MPa

        # fuel properties (default values are for natural gas)
        self.fuel_HHV = fuel_HHV
        self.fuel_CO2 = fuel_CO2

        # dataframe to store data
        rows = range(self.steps)
        self.data = pd.DataFrame(data=0.0, index=rows, columns=attributes_time_series)

        # initialize


    def charge(self, s):
        # update for each caes architecture
        pwr_request = s['pwr_request']

        # calculate
        s['pwr_actual'] = 0.0
        s['heat_input'] = 0.0
        s['m_air'] = 0.0
        s['m_water'] = 0.0
        return s

    def discharge(self, s):
        # update for each caes architecture
        pwr_request = s['pwr_request']

        # calculate
        s['pwr_actual'] = 0.0
        s['heat_input'] = 0.0
        s['m_air'] = 0.0
        s['m_water'] = 0.0
        return s

    def update(self, pwr):
        # keep the same for each caes architecture

        # create series to hold results from current time step
        s = pd.Series(data = 0.0, index=attributes_time_series)
        s['pwr_request'] = pwr
        s['error_msg'] = ''

        # air leakage - to add TODO

        # Charge/discharge
        if pwr < 0.0:  # (charge)
            s = self.charge(s)

        elif pwr > 0.0:  # (discharge)
            s = self.discharge(s)

        # -----------------------
        # check for errors
        # -----------------------
        error_msg = ''
        # check storage pressure against limits
        if self.P_store < self.P_store_min:
            msg = 'Error: P_store < P_store_min'
            s['error_msg'] = s['error_msg'] + msg
            print(msg)
        # check that staying above P_store_min
        if self.P_store > self.P_store_max:
            msg = 'Error: P_store > P_store_max'
            s['error_msg'] = s['error_msg'] + msg
            print(msg)

        # -----------------------
        # save current state
        # -----------------------
        s['P_store'] = self.P_store
        s['T_store'] = self.T_store
        self.data


    def analyze(self):
        # keep the same for each caes architecture

        # compute performance
        pwr_input_total = 0.0 # TODO
        pwr_output_total = 0.0 # TODO
        heat_input_total =  0.0 # TODO
        water_input_total = 0.0 # TODO
        fuel_input_total = heat_input_total / self.fuel_HHV
        CO2_fuel = m_fuel * self.fuel_CO2
        RTE = pwr_output_total / (pwr_input_total + heat_input_total)

        # create series to hold results
        entries = ['RTE', 'CO2', 'fuel', 'water']
        results = pd.Series(index=entries)
        results['RTE'] = RTE
        results['fuel'] = fuel_input_total
        results['CO2'] = CO2_fuel
        results['water'] = water_input_total

        return results
