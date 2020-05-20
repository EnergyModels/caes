# common inputs
gamma = 1.4
Cp = 1.004
Cd = 4.1816
patm = 101.3  # kPa
Ta = 293.15  # K
pHPout = 10  # MPa
pLPout = 1.204  # MPa
Rc = 8.314
Mw = 29  # kg/kmol
Rair = Rc / Mw

# Chris' compressor calculations
MLLP = (1.65 / pLPout - 0.05) * 1
MLHP = (1.65 / pHPout - 0.05) * 5

nLP = gamma * (1 + MLLP * Cd / Cp) / (1 + gamma * MLLP * Cd / Cp)
nHP = gamma * (1 + MLHP * Cd / Cp) / (1 + gamma * MLHP * Cd / Cp)

wLP = nLP * Rair * Ta / (nLP - 1.0) * (1.0 - (pLPout / (patm*1e-3)) ** ((nLP - 1.0) / nLP))  # X
wHP = nHP * Rair * Ta / (nHP - 1.0) * (1.0 - (pHPout / pLPout) ** ((nHP - 1.0) / nHP))  # correct

# Jeff's compressor calculations
p1 = patm  # kPa
p2 = pLPout * 1e3  # kPa
p3 = pHPout * 1e3  # kPa
T1 = Ta
cd = Cd
cp = Cp
k = gamma
R = Rc
M = Mw
nozzles1 = 1.0
nozzles2 = 5.0

ML1 = nozzles1 * (1.65 * 1e3 / p2 - 0.05)  # mass loading
n1 = k * (1 + ML1 * (cd / cp)) / (1 + k * ML1 * (cd / cp))  # polytropic exponent
T2 = T1 * (p2 / p1) ** ((n1 - 1.0) / n1)  # outlet temperature
w_1 = n1 * R / M * T1 / (n1 - 1.0) * (1.0 - (p2 / p1) ** ((n1 - 1) / n1))  # [kJ/kg]


ML2 = nozzles2 * (1.65 * 1e3 / p3 - 0.05)  # mass loading
n2 = k * (1 + ML2 * (cd / cp)) / (1 + k * ML2 * (cd / cp))  # polytropic exponent
T3 = T1 * (p3 / p2) ** ((n2 - 1.0) / n2)  # outlet temperature ( inlet temperature kept at Tatm to match Chris)
w_2 = n2 * R / M * T1 / (n2 - 1.0) * (1.0 - (p3 / p2) ** ((n2 - 1) / n2))  # [kJ/kg] ( inlet temperature kept at Tatm to match Chris)

# report differences
print('LP')
print("ML: " + str(round(MLLP, 3)) + '   ' + str(round(ML1, 3)))
print("n: " + str(round(nLP, 3)) + '   ' + str(round(n1, 3)))
print("w: " + str(round(wLP, 3)) + '   ' + str(round(w_1, 3)))

print('HP')
print("ML: " + str(round(MLHP, 3)) + '   ' + str(round(ML2, 3)))
print("n: " + str(round(nHP, 3)) + '   ' + str(round(n2, 3)))
print("w: " + str(round(wHP, 3)) + '   ' + str(round(w_2, 3)))

