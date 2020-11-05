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
python fixed_expected_case.py
python uncertainty_expected_case.py
python analyze_results_expected_case.py