#!/bin/bash
#
#SBATCH --job-name=Si_band
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1

#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

#SBATCH --partition=ctest       
#SBATCH --account=TRI900128

# Load modules
module purge
spack load quantum-espresso@7.4
module load miniconda3

# Activate your conda env (adjust if needed)
conda activate taiga

# Move to working directory
cd $SLURM_SUBMIT_DIR

# Run simulation
python -m taigacd.core
