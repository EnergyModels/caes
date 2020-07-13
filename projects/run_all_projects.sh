#!/bin/bash

# virginia project
cd virginia/parameter_sweep
sbatch run_parameter_sweep.sh

# return to project directory
cd ../..

# mid_atlantic project
cd mid_atlantic/bct
sbatch run_LK1.sh
sbatch run_MK.sh
sbatch run_UJ1.sh

cd ../monte_carlo
sbatch run_monte_carlo.sh

cd ../sensitivity
sbatch run_sensitivity.sh
