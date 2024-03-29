#!/bin/bash

#SBATCH -J container
#SBATCH -o container.%j.out
#SBATCH -e container.%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --partition=compute
#SBATCH -t 120:00:00

source /contrib/Tim.Smith/miniconda3/etc/profile.d/conda.sh
conda activate ufs2arco
python replay_subsampler_container.py