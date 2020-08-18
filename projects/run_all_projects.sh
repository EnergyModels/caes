#!/bin/bash

# virginia project
cd virginia/sizing_study || exit
sbatch run_sizing_study.sh

# mid_atlantic project
cd ../mid_atlantic || exit

cd ../sensitivity || exit
sbatch run_sensitivity.sh

#cd ../general_monte_carlo || exit
#sbatch run_general_monte_carlo.sh
#
#cd ../sizing_monte_carlo || exit
#sbatch run_sizing_monte_carlo.sh

#cd ../bct_monte_carlo || exit
#sbatch run_bct_monte_carlo.sh

cd ../bct_fixed || exit
sbatch run_bct_fixed.sh
