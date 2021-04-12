#!/bin/bash
#SBATCH -N 1
#SBATCH --cpus-per-task=20
#SBATCH -t 14:00:00
#SBATCH -p standard

module purge
module load anaconda/2019.10-py3.7

# activate environment
source activate caes-py3

# set the NUM_PROCS env variable for the Python script
export NUM_PROCS=$SLURM_CPUS_PER_TASK

# run
python sizing.py
python uncertainty_analysis.py
python analyze_results.py

# plot
python plot_Fig3_storage_potential.py
python plot_Fig5_permeability_thickness.py
python plot_Fig6_select_uncertainty_parameters.py
python plot_FigS2_all_uncertainty_parameters.py
python plot_FigS3_Distance_v_Depth_By_State.py
