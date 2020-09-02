#!/bin/bash

# virginia project
cd virginia/sizing_study || exit
sbatch run_sizing_study.sh

cd ../virginia/sensitivity_all || exit
sbatch run_sensitivity_all.sh

# mid_atlantic project
cd ../mid_atlantic/sensitivity || exit
sbatch run_sensitivity.sh

cd ../mid_atlantic/general_monte_carlo || exit
sbatch run_general_monte_carlo.sh

cd ../mid_atlantic/depth_parameter_sweep || exit
sbatch run_depth_parameter_sweep.sh

cd ../mid_atlantic/sizing_monte_carlo || exit
sbatch run_sizing_monte_carlo.sh

cd ../mid_atlantic/bct_fixed || exit
sbatch run_bct_fixed.sh
#
#cd ../bct_monte_carlo || exit
#sbatch run_bct_monte_carlo.sh