import CoolProp.CoolProp as CP
from caes import pipe_heat_transfer

# inputs
T = 298  # 330.0 # [K]
p = 20.0  # 14.0 # [MPa]
depth = 950  # 1402  # [m]
d = 0.5  # 0.41 # [m]
m_dot = 275  # 300.0 # [kg/s]

# average surface temperature
# avg_depth = depth / 2.0
# m = 0.007376668 * 3.28084
# b = 7.412436
# Ts = 273.15 + m * avg_depth + b  # [K]
Ts = 313

# fluid properties, inputs are degrees K and Pa
rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, "Air")  # density [kg/m3]
mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
Pr = CP.PropsSI('PRANDTL', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
k = CP.PropsSI('CONDUCTIVITY', 'T', T, 'P', p * 1e6, "Air")  # thermal conductivity [W/m/K]
cp = CP.PropsSI('CPMASS', 'T', T, 'P', p * 1e6, "Air")  # heat capacity [J/kg/K]

dT_pipe, Nu, h = pipe_heat_transfer(d=d, m_dot=m_dot, rho=rho, mu=mu, Pr=Pr, k=k, cp=cp, depth=depth,
                                    Tm=T, Ts=Ts)

print('dT_pipe [K] :' + str(dT_pipe))
print('Nu      [-] :' + str(Nu))
print('h  [W/m^-K] :' + str(h))
