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
        inputs = ICAES.get_default_inputs()
        inputs['p_atm'] = cmp_p0  # kPa
        inputs['T_atm'] = 293.15  # K
        inputs['p_store_min'] = cmp_p2  # kPa
        inputs['p_store_init'] = cmp_p2  # kPa
        inputs['p_store_max'] = 20.0e3  # kPa
        inputs['T_store_init'] = 293.15  # K
        inputs['PR_type'] = 'fixed'
        inputs['n_stages_cmp'] = 2
        inputs['PR_cmp'] = [cmp_p1 / cmp_p0, cmp_p2 / cmp_p1]
        inputs['nozzles_cmp'] = [1.0, 5.0]
        inputs['n_stages_exp'] = 2
        inputs['PR_exp'] = [exp_p0 / exp_p1, exp_p1 / exp_p2]
        inputs['nozzles_exp'] = [5.0, 1.0]
        self.sys = ICAES(inputs=inputs)

        # overwrite calculated air and water properties
        self.sys.M = 29
        self.sys.cp = 1.004
        self.sys.k = 1.4
        self.sys.c_water = 4.1816

        # solve two timesteps (index 0 = compression, index 1 = expansion)
        timestep = 1  # [hr]
        pwr = 1000  # [kW]
        self.sys.update(-2.0 * pwr, timestep)
        self.sys.update(1.0 * pwr, timestep)
        self.sys.data.to_csv('test_perf.csv')

    # compresor tests
    def test_cmp_MLLP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_ML0'], 1.321, places=3)

    def test_cmp_MLHP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_ML1'], 0.575, places=3)

    def test_cmp_nLP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_n0'], 1.046, places=3)

    def test_cmp_nHP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_n1'], 1.092, places=3)

    def test_cmp_wLP(self):
        self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_w_stg0'], -219.737, places=3)

    # def test_cmp_wHP(self):
    #     self.assertAlmostEqual(self.sys.data.loc[0, 'cmp_w_stg1'], -208.004, places=3)

    # expander tests
    def test_exp_MLLP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_ML1'], 1.589, places=3)

    def test_exp_MLHP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_ML0'], 0.929, places=3)

    def test_exp_nLP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_n1'], 1.039, places=3)

    def test_exp_nHP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_n0'], 1.062, places=3)

    # def test_exp_wLP(self):
    #     self.assertAlmostEqual(self.sys.data.loc[1, 'exp_w_stg1'], 184.935, places=3)

    def test_exp_wHP(self):
        self.assertAlmostEqual(self.sys.data.loc[1, 'exp_w_stg0'], 154.024, places=3)


if __name__ == '__main__':
    unittest.main()
