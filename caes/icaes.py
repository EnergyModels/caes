import pandas as pd
from caes import CAES
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function


class ICAES(CAES):
    def get_default_inputs():
        inputs = CAES.get_default_inputs()
        # general
        inputs['depth'] = 2.0  # currently unused
        inputs['eta_pump'] = 0.75  # 'fixed' or 'free' pressure ratios
        # machinery
        inputs['PR_type'] = 'free'  # 'fixed' or 'free' pressure ratios
        # compression
        inputs['n_stages_cmp'] = 3
        inputs['PR_cmp'] = [5.0, 5.0, 5.0]
        inputs['nozzles_cmp'] = [1.0, 5.0, 15.0]
        # expansion
        inputs['n_stages_exp'] = 3
        inputs['PR_exp'] = [5.0, 5.0, 5.0]
        inputs['nozzles_exp'] = [15.0, 5.0, 1.0]

        return inputs

    def __init__(self, inputs=get_default_inputs()):
        """
        Initializes a 3 stage near-isothermal CAES system
        """
        CAES.__init__(self, inputs)

        # reservoir
        self.depth = inputs['depth']

        # fluid properties
        self.cp = CP.PropsSI('CPMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR.MIX') / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.cv = CP.PropsSI('CVMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR.MIX') / 1000.0  # constant volume specific heat [kJ/kg-K]
        self.k = self.cp / self.cv  # heat capacity ratio [-]

        # pump
        self.eta_pump = inputs['eta_pump']

        # machinery - general
        if inputs['PR_type'] == 'fixed' or inputs['PR_type'] == 'free':
            self.PR_type = inputs['PR_type']
        else:
            self.PR_type = 'fixed'

        # -------------------
        # compression
        # -------------------
        if inputs['n_stages_cmp'] >= 1:
            self.n_stages_cmp = inputs['n_stages_cmp']
        else:
            self.n_stages_cmp = 1

        # need to make sure the number of PR entries matches the number of stages
        # if not, make an assumption about PR per stage
        if len(inputs['PR_cmp']) == self.n_stages_cmp:
            self.PR_cmp = inputs['PR_cmp']
        else:
            self.PR_cmp = []
            PR_equal = (self.p_store_max / self.p_atm) ** (1. / self.n_stages_cmp)
            for n in range(self.n_stages_cmp):
                self.PR_cmp.append(PR_equal)  # default value of equally divided pressure ratio

        # need to make sure the number of nozzles entries matches the number of stages
        # if not, make an assumption about PR per stage
        if len(inputs['nozzles_cmp']) == self.n_stages_cmp:
            self.nozzles_cmp = inputs['nozzles_cmp']
        else:
            self.nozzles_cmp = []
            for n in range(self.n_stages_cmp):
                self.nozzles_cmp.append(1.0)  # default value of 1 nozzle per stage if not correctly initialized

        # -------------------
        # expansion
        # -------------------

        if inputs['n_stages_exp'] >= 1:
            self.n_stages_exp = inputs['n_stages_exp']
        else:
            self.n_stages_exp = 1

        # need to make sure the number of PR entries matches the number of stages
        # if not, make an assumption about PR per stage
        if len(inputs['PR_exp']) == self.n_stages_exp:
            self.PR_exp = inputs['PR_exp']
        else:
            self.PR_exp = []
            PR_equal = (self.p_store_min / self.p_atm) ** (1. / self.n_stages_exp)
            for n in range(self.n_stages_exp):
                self.PR_exp.append(PR_equal)  # default value of equally divided pressure ratio

        # need to make sure the number of nozzles entries matches the number of stages
        # if not, make an assumption about PR per stage
        if len(inputs['nozzles_exp']) == self.n_stages_exp:
            self.nozzles_exp = inputs['nozzles_exp']
        else:
            self.nozzles_exp = []
            for n in range(self.n_stages_exp):
                self.nozzles_exp.append(1.0)  # default value of 1 nozzle per stage if not correctly initialized

        # recreate dataframe to store data (with additional entries)
        additional_time_series = ['cmp_p_in', 'cmp_T_in', 'exp_p_in', 'exp_T_in']
        stage_entries = ['ML', 'n', 'w_stg', 'w_pmp']
        state_entries = ['p_out', 'T_out']
        for n in range(self.n_stages_cmp):
            for entry in stage_entries:
                additional_time_series.append('cmp_' + entry + str(n))
            for entry in state_entries:
                additional_time_series.append('cmp_' + entry + str(n))
        for n in range(self.n_stages_exp):
            for entry in stage_entries:
                additional_time_series.append('exp_' + entry + str(n))
            for entry in state_entries:
                additional_time_series.append('exp_' + entry + str(n))
        self.attributes_time_series = self.attributes_time_series + additional_time_series
        self.data = pd.DataFrame(columns=self.attributes_time_series)

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
        # --------------
        # fluid properties
        # --------------
        cd = self.c_water  # water - heat capacity [kJ/kg-K]
        cp = self.cp  # air - constant pressure specific heat [kJ/kg-K]
        k = self.k  # air - heat capacity ratio [-]

        # --------------
        # determine stage pressure ratios
        # --------------
        if self.PR_type == 'fixed':
            PRs = self.PR_cmp
        else:  # self.PR_type == 'free'
            PRs = []
            p_in_stg = self.p_atm
            p_out_final = self.p_store
            for PR_design in self.PR_cmp:
                if p_in_stg * PR_design >= p_out_final:
                    PR = p_out_final / p_in_stg
                else:
                    PR = PR_design
                PRs.append(PR)
                # update for next stage
                p_in_stg = p_in_stg * PR

        # --------------
        # inlet
        # --------------
        p_in = self.p_atm
        T_in = self.T_atm
        s['cmp_p_in'] = p_in
        s['cmp_T_in'] = T_in

        # --------------
        # calculate performance for each stage
        # --------------
        for n_stg, nozzles, PR in zip(range(self.n_stages_cmp), self.nozzles_cmp, PRs):
            p_out = p_in * PR
            ML = nozzles * (1.65 * 1e3 / p_out - 0.05)  # mass loading (based on higher pressure)
            n = k * (1 + ML * (cd / cp)) / (1 + k * ML * (cd / cp))  # polytropic exponent
            w_stg = n * self.R / self.M * T_in / (n - 1.0) * (1.0 - (p_out / p_in) ** ((n - 1) / n))  # [kJ/kg]
            w_pmp = - ML * self.v_water * (p_out - self.p_water) / self.eta_pump / 1000.0  # [kJ/kg]
            T_out = T_in * (p_out / p_in) ** ((n - 1.0) / n)  # outlet temperature

            # -------------
            # inlet state for next stage
            # -------------
            p_in = p_out
            T_in = T_out

            # -------------
            # store results
            # -------------
            # required
            s['work_per_kg'] = s['work_per_kg'] + w_stg + w_pmp  # [kJ/kg]
            s['water_per_kg'] = s['water_per_kg'] + ML  # [kg/kg air]
            s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
            # additional
            s['cmp_ML' + str(n_stg)] = ML
            s['cmp_n' + str(n_stg)] = n
            s['cmp_w_stg' + str(n_stg)] = w_stg
            s['cmp_w_pmp' + str(n_stg)] = w_pmp
            s['cmp_p_out' + str(n_stg)] = p_out
            s['cmp_T_out' + str(n_stg)] = T_out

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

        # --------------
        # fluid properties
        # --------------
        cd = self.c_water  # water - heat capacity [kJ/kg-K]
        cp = self.cp  # air - constant pressure specific heat [kJ/kg-K]
        k = self.k  # air - heat capacity ratio [-]

        # --------------
        # determine stage pressure ratios
        # --------------
        if self.PR_type == 'fixed':
            PRs = self.PR_exp
        else:  # self.PR_type == 'free'
            PRs = []
            p_in_stg = self.p_store
            p_out_final = self.p_atm
            for PR_design in self.PR_exp:
                if p_in_stg / PR_design <= p_out_final:
                    PR = p_in_stg / p_out_final
                else:
                    PR = PR_design
                PRs.append(PR)
                # update for next stage
                p_in_stg = p_in_stg / PR

        # --------------
        # inlet
        # --------------
        if self.PR_type == 'free':
            p_in = self.p_store
        else:  # if self.PR_type == 'fixed':
            p_in = self.p_atm
            for PR_design in self.PR_exp:
                p_in = p_in * PR_design  # back-calculate throttle pressure
            if p_in > self.p_store:
                print('expander inlet pressure > storage pressure')
        T_in = self.T_store
        s['exp_p_in'] = p_in
        s['exp_T_in'] = T_in

        # --------------
        # calculate performance for each stage
        # --------------
        for n_stg, nozzles, PR in zip(range(self.n_stages_exp), self.nozzles_exp, PRs):
            p_out = p_in / PR
            ML = nozzles * (1.65 * 1e3 / p_in - 0.05)  # mass loading (based on higher pressure)
            n = k * (1 + ML * (cd / cp)) / (1 + k * ML * (cd / cp))  # polytropic exponent
            w_stg = n * self.R / self.M * T_in / (n - 1.0) * (1.0 - (p_out / p_in) ** ((n - 1) / n))  # [kJ/kg]
            w_pmp = - ML * self.v_water * (p_out - self.p_water) / self.eta_pump / 1000.0  # [kJ/kg]
            T_out = T_in * (p_out / p_in) ** ((n - 1.0) / n)  # outlet temperature

            # -------------
            # inlet state for next stage
            # -------------
            p_in = p_out
            T_in = T_out

            # -------------
            # store results
            # -------------
            # required
            s['work_per_kg'] = s['work_per_kg'] + w_stg + w_pmp  # [kJ/kg]
            s['water_per_kg'] = s['water_per_kg'] + ML  # [kg/kg air]
            s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
            # additional
            s['exp_ML' + str(n_stg)] = ML
            s['exp_n' + str(n_stg)] = n
            s['exp_w_stg' + str(n_stg)] = w_stg
            s['exp_w_pmp' + str(n_stg)] = w_pmp
            s['exp_p_out' + str(n_stg)] = p_out
            s['exp_T_out' + str(n_stg)] = T_out

        return s
