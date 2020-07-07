# caes
Thermodynamic performance of compressed air energy storage (CAES) systems

To install on Rivanna:
- clone from github
    > git clone https://www.github.com/EnergyModels/caes
- move to caes directory
    > cd caes
- load anaconda (may need to update to latest python vversion)
    > module load anaconda/2019.10-py3.7
- create environment
    > conda env create
- activate environment
    > source activate caes-py3
- install caes module
    > cd ~/caes/caes
    > pip install .

To run (from a new terminal)
- load anaconda (may need to update to latest python vversion)
    > module load anaconda/2019.10-py3.7
- activate environment
    > source activate caes-py3
- move to director
    > cd ~/caes/caes/examples/aquifer_sensitivity
- run file
    > python parameter_sweep.py