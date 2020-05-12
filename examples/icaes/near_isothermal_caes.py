from caes import ICAES

pwr = 1000
system = ICAES()
system.single_cycle(pwr)
# system.debug(pwr)
results = system.analyze_performance()
system.data.to_csv('data.csv')
print(results)