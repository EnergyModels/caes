from caes import CAES

pwr = 1000
system = CAES()
system.single_cycle(pwr)
results = system.analyze_performance()
system.data.to_csv('data.csv')
print(results)