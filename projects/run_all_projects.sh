#!/bin/bash

# virginia project
cd virginia/parameter_sweep
sbatch run_parameter_sweep.sh

# return to project directory
cd ../..

# mid_atlantic project
cd mid_atlantic/bct
sbatch run_sizing_study.sh

cd ../monte_carlo_all
sbatch run_monte_carlo_all.sh

cd ../monte_carlo_design
sbatch run_monte_carlo_design.sh

cd ../monte_carlo_reservoir
sbatch run_monte_carlo_reservoir.sh

cd ../sensitivity
sbatch run_sensitivity.sh
