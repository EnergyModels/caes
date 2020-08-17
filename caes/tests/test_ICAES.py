import unittest
from caes import ICAES


class TestICAES(unittest.TestCase):

    def setUp(self):
        # calculate stage pressures
        cmp_p0 = 101.3  # kPa
        cmp_p2 = 10.0e3  # kPa
        cmp_p1 = (1.43 * cmp_p0 * cmp_p2) ** 0.5  # kPa

        exp_p0 = 7.0e3  # kPa
        exp_p2 = 101.3  # kPa
        exp_p1 = (1.43 * exp_p0 * exp_p2) ** 0.5  # kPa

        # test conditions
        T_atm_K = 293.15
        T_atm_C = T_atm_K - 273.15
        inputs = ICAES.get_default_inputs()
        inputs['p_atm'] = cmp_p0  # kPa
        inputs['T_atm'] = T_atm_C  # C
        inputs['depth'] = 900.0 # [m]
        inputs['PR_type'] = 'fixed'
        # inputs['n_stages_cmp'] = 2
        inputs['PR_cmp'] = [cmp_p1 / cmp_p0, cmp_p2 / cmp_p1]
        inputs['ML_cmp1'] = 1.0*(1.65/(cmp_p1/1000)-0.05)
        inputs['ML_cmp2'] = 5.0*(1.65/(cmp_p2/1000)-0.05)
        inputs['ML_cmp3'] = -1.0
        # inputs['n_stages_exp'] = 2
        inputs['PR_exp'] = [exp_p0 / exp_p1, exp_p1 / exp_p2]
        inputs['ML_exp1'] = 5.0*(1.65/(exp_p0/1000)-0.05)
        inputs['ML_exp2'] = 1.0*(1.65/(exp_p1/1000)-0.05)
        inputs['ML_exp3'] = -1.0
        self.sys = ICAES(inputs=inputs)

        # overwrite calculated air and water properties
        self.sys.M = 29.0
        self.sys.cp = 1.004
        self.sys.gamma = 1.4
        self.sys.c_water = 4.1816
        self.sys.T_store_init = T_atm_K  # [K]
        self.sys.T_store = T_atm_K  # [K]
        self.sys.T2 = T_atm_K  # [K]
        self.sys.T3 = T_atm_K  # [K]
        self.sys.m_store =self.sys.m_store * 1.2 # increase amount of air to stay within pressure limits

        # solve two timesteps (index 0 = compression, index 1 = expansion)
        self.sys.update(m_dot=10.0, delta_t=2.0)
        self.sys.update(m_dot=-10.0, delta_t=1.0)
        self.sys.data.to_csv('test_perf.csv')
        # self.data.to_csv('single_cycle_timeseries.csv')

    # compresor tests
    def test_cmp_nLP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_n0'], 1.046, places=3)

    def test_cmp_nHP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_n1'], 1.092, places=3)

    def test_cmp_wLP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_w_stg0'], -219.737, places=3)

    # expander tests
    def test_exp_nLP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_n1'], 1.039, places=3)

    def test_exp_nHP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_n0'], 1.062, places=3)

    def test_exp_wHP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_w_stg0'], 154.024, places=3)


if __name__ == '__main__':
    unittest.main()
