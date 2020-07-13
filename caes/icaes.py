import pandas as pd
from caes import CAES
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function


class ICAES(CAES):
    def get_default_inputs():
        inputs = CAES.get_default_inputs()
        # general
        inputs['eta_pump'] = 0.75
        # machinery
        inputs['PR_type'] = 'free'  # 'fixed' or 'free' pressure ratios
        # compression
        # inputs['n_stages_cmp'] = 3
        inputs['nozzles_cmp1'] = 1
        inputs['nozzles_cmp2'] = 5
        inputs['nozzles_cmp3'] = 15
        inputs['nozzles_cmp4'] = 0  # 0 - unused
        inputs['nozzles_cmp5'] = 0  # 0 - unused
        # expansion
        # inputs['n_stages_exp'] = 3
        inputs['nozzles_exp1'] = 15
        inputs['nozzles_exp2'] = 5
        inputs['nozzles_exp3'] = 1
        inputs['nozzles_exp4'] = 0  # 0 - unused
        inputs['nozzles_exp5'] = 0  # 0 - unused

        return inputs

    def __init__(self, inputs=get_default_inputs()):
        """
        Initializes a mulit-stage near-isothermal CAES system
        """
        CAES.__init__(self, inputs)

        # reservoir
        self.depth = inputs['depth']

        # fluid properties
        self.cp = CP.PropsSI('CPMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR') / 1000.0  # constant pressure specific heat [kJ/kg-K]
        self.cv = CP.PropsSI('CVMASS', 'T', self.T_atm, 'P', self.p_atm * 1000.0,
                             'AIR') / 1000.0  # constant volume specific heat [kJ/kg-K]
        self.gamma = self.cp / self.cv  # heat capacity ratio [-]

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
        # number of compression stages, stops at first 0, negative or non-integer entry for nozzles
        # need to make sure the number of nozzles entries matches the number of stages
        if inputs['nozzles_cmp1'] < 1 or not isinstance(inputs['nozzles_cmp1'], int):
            self.n_stages_cmp = 1
            self.nozzles_cmp = [1]

        elif inputs['nozzles_cmp2'] < 1 or not isinstance(inputs['nozzles_cmp2'], int):
            self.n_stages_cmp = 1
            self.nozzles_cmp = [inputs['nozzles_cmp1']]

        elif inputs['nozzles_cmp3'] < 1 or not isinstance(inputs['nozzles_cmp3'], int):
            self.n_stages_cmp = 2
            self.nozzles_cmp = [inputs['nozzles_cmp1'], inputs['nozzles_cmp2']]

        elif inputs['nozzles_cmp4'] < 1 or not isinstance(inputs['nozzles_cmp4'], int):
            self.n_stages_cmp = 3
            self.nozzles_cmp = [inputs['nozzles_cmp1'], inputs['nozzles_cmp2'], inputs['nozzles_cmp3']]

        elif inputs['nozzles_cmp5'] < 1 or not isinstance(inputs['nozzles_cmp5'], int):
            self.n_stages_cmp = 4
            self.nozzles_cmp = [inputs['nozzles_cmp1'], inputs['nozzles_cmp2'], inputs['nozzles_cmp3'],
                                inputs['nozzles_cmp4']]

        else:
            self.n_stages_cmp = 5
            self.nozzles_cmp = [inputs['nozzles_cmp1'], inputs['nozzles_cmp2'], inputs['nozzles_cmp3'],
                                inputs['nozzles_cmp4'], inputs['nozzles_cmp5']]

        # # inputs['n_stages_cmp'] = 3
        # if inputs['n_stages_cmp'] >= 1:
        #     self.n_stages_cmp = inputs['n_stages_cmp']
        # else:
        #     self.n_stages_cmp = 1

        # equally divide pressure ratio for each stage
        PR_equal = (self.p_store_max / self.p_atm) ** (1. / self.n_stages_cmp)
        self.PR_cmp = []
        for n in range(self.n_stages_cmp):
            self.PR_cmp.append(PR_equal)

        # if not, make an assumption about PR per stage
        # if len(inputs['nozzles_cmp']) == self.n_stages_cmp:
        #     self.nozzles_cmp = inputs['nozzles_cmp']
        # else:
        #     self.nozzles_cmp = []
        #     for n in range(self.n_stages_cmp):
        #         self.nozzles_cmp.append(1.0)  # default value of 1 nozzle per stage if not correctly initialized

        # -------------------
        # expansion
        # -------------------
        if inputs['nozzles_exp1'] < 1 or not isinstance(inputs['nozzles_exp1'], int):
            self.n_stages_exp = 1
            self.nozzles_exp = [1]

        elif inputs['nozzles_exp2'] < 1 or not isinstance(inputs['nozzles_exp2'], int):
            self.n_stages_exp = 1
            self.nozzles_exp = [inputs['nozzles_exp1']]

        elif inputs['nozzles_exp3'] < 1 or not isinstance(inputs['nozzles_exp3'], int):
            self.n_stages_exp = 2
            self.nozzles_exp = [inputs['nozzles_exp1'], inputs['nozzles_exp2']]

        elif inputs['nozzles_exp4'] < 1 or not isinstance(inputs['nozzles_exp4'], int):
            self.n_stages_exp = 3
            self.nozzles_exp = [inputs['nozzles_exp1'], inputs['nozzles_exp2'], inputs['nozzles_exp3']]

        elif inputs['nozzles_exp5'] < 1 or not isinstance(inputs['nozzles_exp5'], int):
            self.n_stages_exp = 4
            self.nozzles_exp = [inputs['nozzles_exp1'], inputs['nozzles_exp2'], inputs['nozzles_exp3'],
                                inputs['nozzles_exp4']]

        else:
            self.n_stages_exp = 5
            self.nozzles_exp = [inputs['nozzles_exp1'], inputs['nozzles_exp2'], inputs['nozzles_exp3'],
                                inputs['nozzles_exp4'], inputs['nozzles_exp5']]
        # # inputs['n_stages_exp'] = 3
        # if inputs['n_stages_exp'] >= 1:
        #     self.n_stages_exp = inputs['n_stages_exp']
        # else:
        #     self.n_stages_exp = 1

        # equally divide pressure ratio for each stage
        PR_equal = (self.p_store_max / self.p_atm) ** (1. / self.n_stages_exp)
        self.PR_exp = []
        for n in range(self.n_stages_exp):
            self.PR_exp.append(PR_equal)

        # # need to make sure the number of nozzles entries matches the number of stages
        # # if not, make an assumption about PR per stage
        # if len(inputs['nozzles_exp']) == self.n_stages_exp:
        #     self.nozzles_exp = inputs['nozzles_exp']
        # else:
        #     self.nozzles_exp = []
        #     for n in range(self.n_stages_exp):
        #         self.nozzles_exp.append(1.0)  # default value of 1 nozzle per stage if not correctly initialized

        # -------------------
        # recreate dataframe to store data (with additional entries)
        # -------------------
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
        gamma = self.gamma  # air - heat capacity ratio [-]

        # --------------
        # determine stage pressure ratios
        # --------------
        if self.PR_type == 'fixed':
            PRs = self.PR_cmp
        else:  # self.PR_type == 'free'
            PRs = []
            p_in_stg = s['p0']
            p_out_final = s['p1']
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
        p_in = s['p0']
        T_in = self.T_atm
        s['cmp_p_in'] = p_in
        s['cmp_T_in'] = T_in

        # --------------
        # calculate performance for each stage
        # --------------
        for n_stg, nozzles, PR in zip(range(self.n_stages_cmp), self.nozzles_cmp, PRs):
            p_out = p_in * PR
            ML = nozzles * (1.65 / p_out - 0.05)  # mass loading (based on higher pressure)
            n = gamma * (1 + ML * (cd / cp)) / (1 + gamma * ML * (cd / cp))  # polytropic exponent
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
        gamma = self.gamma  # air - heat capacity ratio [-]

        # --------------
        # determine stage pressure ratios
        # --------------
        if self.PR_type == 'fixed':
            PRs = self.PR_exp
        else:  # self.PR_type == 'free'
            PRs = []
            p_in_stg = s['p1']
            p_out_final = s['p0']
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
            p_in = s['p1']
        else:  # if self.PR_type == 'fixed':
            p_in = s['p0']
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
            ML = nozzles * (1.65 / p_in - 0.05)  # mass loading (based on higher pressure)
            n = gamma * (1 + ML * (cd / cp)) / (1 + gamma * ML * (cd / cp))  # polytropic exponent
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
