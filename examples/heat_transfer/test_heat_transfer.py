import CoolProp.CoolProp as CP
from caes import pipe_heat_transfer_subsurface, pipe_heat_transfer_ocean

# ==========================================
# Run at default conditions
# ==========================================
print("\n\ndefault conditions\n")
dT_pipe1 = pipe_heat_transfer_subsurface(debug=True)

# ==========================================
# Run at expected conditions (coming up pipe)
# ==========================================
# inputs
T = 314.0  # [K]
p = 17.34  # [MPa]
depth = 1402.35  # [m]
r_pipe = 0.41 / 2.0  # [m]
m_dot = 491.27  # [kg/s]

# average surface temperature
avg_depth = depth / 2.0
m = 0.007376668 * 3.28084
b = 7.412436
Ts = 273.15 + m * avg_depth + b  # [K]

# fluid properties, inputs are degrees K and Pa
rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, "Air")  # density [kg/m3]
mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
Pr = CP.PropsSI('PRANDTL', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
k = CP.PropsSI('CONDUCTIVITY', 'T', T, 'P', p * 1e6, "Air")  # thermal conductivity [W/m/K]
cp = CP.PropsSI('CPMASS', 'T', T, 'P', p * 1e6, "Air")  # heat capacity [J/kg/K]

# perform calculations
print("\n\nExpected conditions\n")
dT_pipe2 = pipe_heat_transfer_subsurface(r_pipe=r_pipe, m_dot=m_dot, rho=rho, mu=mu, Pr=Pr, k_air=k, cp=cp, depth=depth,
                              Tm=T, Ts=Ts, debug=True)

# ==========================================
# Run to match Juliet's calculations (coming up pipe)
# ==========================================
# inputs
T = 314.0  # 330.0 # [K]
p = 17.34  # 14.0 # [MPa]
depth = 1402.35  # 1402  # [m]
r_pipe = 0.41 / 2.0  # [m]
m_dot = 491.27  # [kg/s]

# average surface temperature
Ts = 311  # [K]

# fluid properties, inputs are degrees K and Pa
rho = 186.05  # density [kg/m3]
mu = 0.000023  # viscosity [Pa*s]
Pr = 0.796  # viscosity [Pa*s]
k = 0.0362  # thermal conductivity [W/m/K]
cp = 1230.0  # heat capacity [J/kg/K]

print("\n\nMatching Juliet's calculations\n")
dT_pipe3 = pipe_heat_transfer_subsurface(r_pipe=r_pipe, m_dot=m_dot, rho=rho, mu=mu, Pr=Pr, k_air=k, cp=cp, depth=depth,
                              Tm=T, Ts=Ts, debug=True)

# ==========================================
# Run at water conditions (coming up pipe)
# ==========================================
# inputs
T = 314.0  # [K]
p = 17.34  # [MPa]
depth = 25.0  # [m]
r_pipe = 0.41 / 2.0  # [m]
m_dot = 491.27  # [kg/s]

# average surface temperature
Ts = 290  # [K]

# fluid properties, inputs are degrees K and Pa
rho = CP.PropsSI('D', 'T', T, 'P', p * 1e6, "Air")  # density [kg/m3]
mu = CP.PropsSI('V', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
Pr = CP.PropsSI('PRANDTL', 'T', T, 'P', p * 1e6, "Air")  # viscosity [Pa*s]
k = CP.PropsSI('CONDUCTIVITY', 'T', T, 'P', p * 1e6, "Air")  # thermal conductivity [W/m/K]
cp = CP.PropsSI('CPMASS', 'T', T, 'P', p * 1e6, "Air")  # heat capacity [J/kg/K]

# perform calculations
print("\n\nExpected conditions for ocean heat transfer\n")
dT_pipe4 = pipe_heat_transfer_ocean(r_pipe=r_pipe, m_dot=m_dot, rho=rho, mu=mu, Pr=Pr, k_air=k, cp=cp, depth=depth,
                              Tm=T, Ts=Ts, debug=True)
