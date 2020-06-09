import math

t =1
Q_well = 1
H = 1
phi = 1
k = 1
S_res = 1

mu_c = 1
mu_w = 1

k_c = k
k_w = k

eta = r / k**0.5
lambda_c = k_c / mu_c
lambda_w = k_w / mu_w


tau = Q_well*t/(2*math.pi*H*phi*k*(1-S_res))
lambda_ratio = lambda_c / lambda_w
chi = eta**2/tau

def h(lambda_ratio, chi):
