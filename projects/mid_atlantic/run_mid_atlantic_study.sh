#!/bin/bash

# main study
cd study || exit
sbatch run_study.sh

# sensitivity analysis
cd ../sensitivity_single_site || exit
sbatch run_sensitivity.sh

cd ../sensitivity_site_comparison || exit
sbatch run_sensitivity_comparison.sh

# supporting figures
cd ../aquifer_flow || exit
sbatch run_aquifer_flow.sh

cd ../sample || exit
sbatch run_sample.py
