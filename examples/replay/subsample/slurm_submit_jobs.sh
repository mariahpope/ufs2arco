#!/bin/bash

#SBATCH -J subsample_$1
#SBATCH -o subsample_%j.out
#SBATCH -e subsample_%j.err
#SBATCH -t 120:00:00
#SBATCH --partition=compute
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=30

source /contrib/Mariah.Pope/miniconda3/etc/profile.d/conda.sh
conda activate base
python subsampler.py $1 $2