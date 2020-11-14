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
        inputs['PR_cmp'] = []  # leave empty for equal pressure ratios, otherwise specify per stage
        inputs['PR_exp'] = []

        # compression - mass load per stage (ratio of water to air by mass)
        inputs['ML_cmp1'] = 2.0
        inputs['ML_cmp2'] = 1.5
        inputs['ML_cmp3'] = 1.0
        inputs['ML_cmp4'] = -1  # <0 - unused
        inputs['ML_cmp5'] = -1  # <0 - unused

        # expansion - mass loading per stage
        inputs['ML_exp1'] = 1.0
        inputs['ML_exp2'] = 1.5
        inputs['ML_exp3'] = 2.0
        inputs['ML_exp4'] = -1  # <0 - unused
        inputs['ML_exp5'] = -1  # <0 - unused

        # compression - pressure drop inbetween stages (fraction)
        inputs['delta_p_cmp12'] = 0.01  # between stages 1 and 2
        inputs['delta_p_cmp23'] = 0.01
        inputs['delta_p_cmp34'] = -1  # <0 - unused
        inputs['delta_p_cmp45'] = -1  # <0 - unused

        # compression - pressure drop inbetween stages (fraction)
        inputs['delta_p_exp12'] = 0.01  # between stages 1 and 2
        inputs['delta_p_exp23'] = 0.01
        inputs['delta_p_exp34'] = -1  # <0 - unused
        inputs['delta_p_exp45'] = -1  # <0 - unused

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
        # number of compression stages, stops at first 0, negative or non-integer entry for ML
        # need to make sure the number of ML entries matches the number of stages
        if inputs['ML_cmp1'] < 0:
            self.n_stages_cmp = 1
            self.ML_cmp = [1]

        elif inputs['ML_cmp2'] < 0:
            self.n_stages_cmp = 1
            self.ML_cmp = [inputs['ML_cmp1']]

        elif inputs['ML_cmp3'] < 0:
            self.n_stages_cmp = 2
            self.ML_cmp = [inputs['ML_cmp1'], inputs['ML_cmp2']]

        elif inputs['ML_cmp4'] < 0:
            self.n_stages_cmp = 3
            self.ML_cmp = [inputs['ML_cmp1'], inputs['ML_cmp2'], inputs['ML_cmp3']]

        elif inputs['ML_cmp5'] < 0:
            self.n_stages_cmp = 4
            self.ML_cmp = [inputs['ML_cmp1'], inputs['ML_cmp2'], inputs['ML_cmp3'],
                           inputs['ML_cmp4']]
        else:
            self.n_stages_cmp = 5
            self.ML_cmp = [inputs['ML_cmp1'], inputs['ML_cmp2'], inputs['ML_cmp3'],
                           inputs['ML_cmp4'], inputs['ML_cmp5']]

        # interstage pressure drop
        self.delta_p_cmp = []
        for i in range(self.n_stages_cmp):
            if i == 0 and inputs['delta_p_cmp12'] > 0.0 and self.include_interstage_dp:
                self.delta_p_cmp.append(inputs['delta_p_cmp12'])
            elif i == 1 and inputs['delta_p_cmp23'] > 0.0 and self.include_interstage_dp:
                self.delta_p_cmp.append(inputs['delta_p_cmp23'])
            elif i == 2 and inputs['delta_p_cmp34'] > 0.0 and self.include_interstage_dp:
                self.delta_p_cmp.append(inputs['delta_p_cmp34'])
            elif i == 3 and inputs['delta_p_cmp45'] > 0.0 and self.include_interstage_dp:
                self.delta_p_cmp.append(inputs['delta_p_cmp45'])
            else:
                self.delta_p_cmp.append(0.0)

        # multiplier for total pressure ratio to account for interstage pressure drops
        PR_delta_p_cmp = 1.0
        for delta_p in self.delta_p_cmp:
            PR_delta_p_cmp = PR_delta_p_cmp * (1.0 + delta_p)

        # equally divide pressure ratio for each stage, if pressure ratios are unspecified
        if len(inputs['PR_cmp']) == self.n_stages_cmp:
            self.PR_cmp = inputs['PR_cmp']
        else:
            self.PR_cmp = []
            PR_equal = (self.p_machine_design / self.p_atm * PR_delta_p_cmp) ** (1. / self.n_stages_cmp)
            for n in range(self.n_stages_cmp):
                self.PR_cmp.append(PR_equal)

        # -------------------
        # expansion
        # -------------------
        if inputs['ML_exp1'] < 0:
            self.n_stages_exp = 1
            self.ML_exp = [1]

        elif inputs['ML_exp2'] < 0:
            self.n_stages_exp = 1
            self.ML_exp = [inputs['ML_exp1']]

        elif inputs['ML_exp3'] < 0:
            self.n_stages_exp = 2
            self.ML_exp = [inputs['ML_exp1'], inputs['ML_exp2']]

        elif inputs['ML_exp4'] < 0:
            self.n_stages_exp = 3
            self.ML_exp = [inputs['ML_exp1'], inputs['ML_exp2'], inputs['ML_exp3']]

        elif inputs['ML_exp5'] < 0:
            self.n_stages_exp = 4
            self.ML_exp = [inputs['ML_exp1'], inputs['ML_exp2'], inputs['ML_exp3'],
                           inputs['ML_exp4']]
        else:
            self.n_stages_exp = 5
            self.ML_exp = [inputs['ML_exp1'], inputs['ML_exp2'], inputs['ML_exp3'],
                           inputs['ML_exp4'], inputs['ML_exp5']]

        # interstage pressure drop
        self.delta_p_exp = []
        for i in range(self.n_stages_exp):
            if i == 0 and inputs['delta_p_exp12'] > 0.0 and self.include_interstage_dp:
                self.delta_p_exp.append(inputs['delta_p_exp12'])
            elif i == 1 and inputs['delta_p_exp23'] > 0.0 and self.include_interstage_dp:
                self.delta_p_exp.append(inputs['delta_p_exp23'])
            elif i == 2 and inputs['delta_p_exp34'] > 0.0 and self.include_interstage_dp:
                self.delta_p_exp.append(inputs['delta_p_exp34'])
            elif i == 3 and inputs['delta_p_exp45'] > 0.0 and self.include_interstage_dp:
                self.delta_p_exp.append(inputs['delta_p_exp45'])
            else:
                self.delta_p_exp.append(0.0)

        # multiplier for total pressure ratio to account for interstage pressure drops
        PR_delta_p_exp = 1.0
        for delta_p in self.delta_p_exp:
            PR_delta_p_exp = PR_delta_p_exp * (1.0 + delta_p)

        # equally divide pressure ratio for each stage, if pressure ratios are unspecified
        if len(inputs['PR_exp']) == self.n_stages_exp:
            self.PR_exp = inputs['PR_exp']
        else:
            self.PR_exp = []
            PR_equal = (self.p_machine_design / self.p_atm * PR_delta_p_exp) ** (1. / self.n_stages_exp)
            for n in range(self.n_stages_exp):
                self.PR_exp.append(PR_equal)

        # -------------------
        # recreate dataframe to store data (with additional entries)
        # -------------------
        additional_time_series = ['cmp_p_in', 'cmp_T_in', 'exp_p_in', 'exp_T_in']
        stage_entries = ['ML', 'n', 'w_stg', 'w_pmp']
        state_entries = ['p_in', 'T_in', 'p_out', 'T_out']
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
        T_in = s['T0']
        s['cmp_p_in'] = p_in
        s['cmp_T_in'] = T_in

        # --------------
        # calculate performance for each stage
        # --------------
        for n_stg, ML, PR, delta_p in zip(range(self.n_stages_cmp), self.ML_cmp, PRs, self.delta_p_cmp):
            p_out = p_in * PR
            n = gamma * (1 + ML * (cd / cp)) / (1 + gamma * ML * (cd / cp))  # polytropic exponent
            w_stg = n * self.R / self.M * T_in / (n - 1.0) * (1.0 - (p_out / p_in) ** ((n - 1) / n))  # [kJ/kg]
            w_pmp = - ML * self.v_water * (p_out - self.p_water) / self.eta_pump / 1000.0  # [kJ/kg]
            T_out = T_in * (p_out / p_in) ** ((n - 1.0) / n)  # outlet temperature

            # -------------
            # store results
            # -------------
            # required
            s['work_per_kg'] = s['work_per_kg'] + w_stg + w_pmp  # [kJ/kg]
            s['water_per_kg'] = s['water_per_kg'] + ML  # [kg/kg air]
            s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
            # additional
            s['cmp_p_in' + str(n_stg)] = p_in
            s['cmp_T_in' + str(n_stg)] = T_in
            s['cmp_ML' + str(n_stg)] = ML
            s['cmp_n' + str(n_stg)] = n
            s['cmp_w_stg' + str(n_stg)] = w_stg
            s['cmp_w_pmp' + str(n_stg)] = w_pmp
            s['cmp_p_out' + str(n_stg)] = p_out
            s['cmp_T_out' + str(n_stg)] = T_out

            # -------------
            # inlet state for next stage
            # -------------
            p_in = p_out * (1.0 - delta_p)
            T_in = T_out

        s['T1'] = T_out
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
            if p_in / 1000.0 > self.p_store:
                print('expander inlet pressure > storage pressure')
        T_in = s['T1']
        s['exp_p_in'] = p_in
        s['exp_T_in'] = T_in

        # --------------
        # calculate performance for each stage
        # --------------
        for n_stg, ML, PR, delta_p in zip(range(self.n_stages_exp), self.ML_exp, PRs, self.delta_p_exp):
            p_out = p_in / PR
            n = gamma * (1 + ML * (cd / cp)) / (1 + gamma * ML * (cd / cp))  # polytropic exponent
            w_stg = n * self.R / self.M * T_in / (n - 1.0) * (1.0 - (p_out / p_in) ** ((n - 1) / n))  # [kJ/kg]
            w_pmp = - ML * self.v_water * (p_out - self.p_water) / self.eta_pump / 1000.0  # [kJ/kg]
            T_out = T_in * (p_out / p_in) ** ((n - 1.0) / n)  # outlet temperature

            # -------------
            # store results
            # -------------
            # required
            s['work_per_kg'] = s['work_per_kg'] + w_stg + w_pmp  # [kJ/kg]
            s['water_per_kg'] = s['water_per_kg'] + ML  # [kg/kg air]
            s['fuel_per_kg'] = 0.0  # near-isothermal - no heat input [kg/kg air]
            # additional
            s['exp_p_in' + str(n_stg)] = p_in
            s['exp_T_in' + str(n_stg)] = T_in
            s['exp_ML' + str(n_stg)] = ML
            s['exp_n' + str(n_stg)] = n
            s['exp_w_stg' + str(n_stg)] = w_stg
            s['exp_w_pmp' + str(n_stg)] = w_pmp
            s['exp_p_out' + str(n_stg)] = p_out
            s['exp_T_out' + str(n_stg)] = T_out

            # -------------
            # inlet state for next stage
            # -------------
            p_in = p_out * (1.0 - delta_p)
            T_in = T_out

        s['T0'] = T_out
        return s
