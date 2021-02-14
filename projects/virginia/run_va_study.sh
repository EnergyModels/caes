#!/bin/bash

# main study
cd sizing_study || exit
sbatch run_sizing_study.sh

# sensitivity analysis
cd ../sensitivity || exit
sbatch run_sensitivity.sh

# sample run
cd ../sample || exit
sbatch run_sample.sh

# analyze loss mechanisms
cd ../loss_mechanisms || exit
sbatch run_quantify_losses.sh


