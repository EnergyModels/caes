from caes import aquifer_dp
import CoolProp.CoolProp as CP  # http://www.coolprop.org/coolprop/HighLevelAPI.html#propssi-function

# fixed inputs
r_w = 0.265  # [m]
h = 62.44  # m
T = 298.15  # [K]

# variables
m_dot = 325.872235685705  # [kg/s]
p_f = 14.02  # [MPa]
k = 0.47  # [mD] (range based on Sopher et al. 2019)
r_f = 359.738666178019  # [m]

rho = CP.PropsSI('D', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')  # [kg/m3] inputs are degrees K and Pa
mu = CP.PropsSI('V', 'T', T, 'P', p_f * 1e6, 'AIR.MIX') * 1000  # convert Pa*s (output) to cP
Z = CP.PropsSI('Z', 'T', T, 'P', p_f * 1e6, 'AIR.MIX')
Q = m_dot / rho
delta_p = aquifer_dp(Q=Q, p_f=p_f, r_f=r_f, r_w=r_w, k=k, h=h, mu=mu, T=T, Z=Z)
print(delta_p)
