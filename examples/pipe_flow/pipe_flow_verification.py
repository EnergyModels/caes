from math import pi
from caes import pipe_grav_dp, pipe_fric_dp

# ====================
# verification case
# ====================
# inputs
depth = 950  # depth [m]
d = 0.53  # diameter [m]
rho = 233.740332241268  # [kg/m^3]
mu = 0.00001837  # [Pa*s]
U = 10  # velocity [m/s]
epsilon = 0.002e-3  # roughness [m]

# expected values
dp_grav_exp = -2.17834302632249  # [MPa]
dp_fric_exp = 0.153697078405405  # [MPa]
f_exp = 0.007337

# pre-process
A = pi/4*d**2
m_dot = rho*A*U

# perform calculationss
dp_fric, f = pipe_fric_dp(epsilon=epsilon, d=d, depth=depth, m_dot=m_dot, rho=rho, mu=mu)
dp_grav = pipe_grav_dp(m_dot=m_dot, rho=rho, z=depth)

# calculate difference
pct_diff_f = (f - f_exp) / f_exp
pct_diff_dp_fric = (dp_fric - dp_fric_exp) / dp_fric_exp
pct_diff_dp_grav = (dp_grav - dp_grav_exp) / dp_grav_exp

# print results
print('Percent difference [%]')
print('Friction coefficient  : '+str(pct_diff_f))
print('Friction pressure drop: '+str(pct_diff_dp_fric))
print('Gravity pressure drop : '+str(pct_diff_dp_grav))