#!/bin/bash

#SBATCH -J memory
#SBATCH -o memory.%j.out
#SBATCH -e memory.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --partition=compute
#SBATCH -t 120:00:00

source /contrib/Mariah.Pope/miniconda3/etc/profile.d/conda.sh
conda activate ufs2arco
python test_memory.py