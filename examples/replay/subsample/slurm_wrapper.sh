#!/bin/bash

total_timesteps=87020
jobs_to_submit=15

# Calculate the number of timesteps each job should process
let "timesteps_per_job = total_timesteps / jobs_to_submit"

for (( i=0; i<jobs_to_submit; i++ ))
do
    let "start = i * timesteps_per_job"
    let "end = start + timesteps_per_job - 1"

    # Adjust the last job to ensure it includes any remaining timesteps
    if [ $i -eq $((jobs_to_submit - 1)) ]; then
        let "end = total_timesteps - 1"
    fi
    
    sbatch slurm_submit_jobs.sh $start $end
done