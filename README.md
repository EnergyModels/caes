# caes
Thermodynamic performance of isothermal offshore compressed air energy storage (OCAES) systems

## Installation
Sample linux installion based on Rivanna, the UVA High Performance Computer https://www.rc.virginia.edu/
  - clone from github
      > git clone https://www.github.com/EnergyModels/caes
  - move to caes directory
      > cd caes
  - load anaconda (may need to update to latest python version)
      > module load anaconda/2019.10-py3.7
  - create environment
      > conda env create
  - activate environment
      > source activate caes-py3
  - install caes module
      > cd ~/caes/caes
      > pip install .

## Operation
To run (from a new terminal) on Rivanna
- load anaconda (may need to update to latest python vversion)
    > module load anaconda/2019.10-py3.7
- activate environment
    > source activate caes-py3
- move to directory
    > cd ~/caes/caes/projects/sample
- run file
    > python sample.py

## Projects

### Techno-economic analysis of offshore isothermal compressed air energy storage in saline aquifers co-located with wind power

  Bennett, J.A., Simpson, J.G., Qin, C., Fittro, R., Koenig, G.M., Clarens, A.F., Loth, E. (in review). Techno-economic 
  analysis of offshore isothermal compressed air energy storage in saline aquifers co-located with wind power.

    cd caes\projects\virginia 
    sbatch run_va_study.sh

### Frontiers in Offshore Compressed Air Energy Storage Could Support the Energy Transition
  
  Bennett, J.A., Fitts, J.P., Clarens, A.F. (in prep). Frontiers in Offshore Compressed Air Energy Storage Could 
  Support the Energy Transition.

    cd caes\projects\mid_atlantic
    sbatch run_mid_atlantic_study.sh

## Acknowledgement
Special thank you to Laura Keister and Neeraj Gupta from Battelle for sharing the geophysical parameters of the Baltimore Canyon Trough.
If you use the data (Battelle_data.xlsx, located in caes/projects/mid_atlantic/study), please consider citing:

  Fukai, I., Keister, L, Ganesh, P.R., Cumming, L., Fortin, W., and Gupta, N. (2020). Carbon dioxide storage resource 
  assessment of Cretaceous- and Jurassic-age sandstones in the Atlantic offshore region of the northeastern United 
  States, Environmental Geosciences, 27 (1): 25-47. https://doi.org/10.1306/eg.09261919016

  Battelle, Delaware Geological Survey, Maryland Geological Survey, Pennsylvania Geological Survey, United States 
  Geological Survey, Lamont-Doherty Earth Observatory at Columbia University, and Rutgers University (2019). 
  Mid-Atlantic U.S. Offshore Carbon Storage Resource Assessment Project Task 6 Risk Factor Analysis Report. DOE 
  Cooperative Agreement No. DE-FE0026087.
