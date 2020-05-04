from setuptools import setup

setup(name='estorage',
      version='0.0.1',
      description='Thermodynamic performance of compressed air energy storage (CAES) systems',
      url='https://github.com/EnergyModels/caes',
      author='Jeff Bennett',
      author_email='jab6ft@virginia.edu',
      license='MIT',
      packages=['caes'],
      zip_safe=False,
      install_requires=['CoolProp', 'pandas', 'numpy', 'seaborn'])
