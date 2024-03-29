import xarray as xr
import gcsfs
import zarr
import numpy as np
import dask.array as darray
from replay_subsampler_utils import move_one_job
import os
import subprocess

def submit_slurm_mover(job_id):

    the_code = \
        f"from replay_subsampler_utils import move_one_job\n"+\
        f"move_one_job(0,20,4)"

    slurm_dir = "slurm/replay-1.00-degree"
    txt = "#!/bin/bash\n\n" +\
        f"#SBATCH -J r1d{job_id:03d}\n"+\
        f"#SBATCH -o {slurm_dir}/{job_id:03d}.%j.out\n"+\
        f"#SBATCH -e {slurm_dir}/{job_id:03d}.%j.err\n"+\
        f"#SBATCH --nodes=1\n"+\
        f"#SBATCH --ntasks=1\n"+\
        f"#SBATCH --cpus-per-task=30\n"+\
        f"#SBATCH --partition=compute\n"+\
        f"#SBATCH -t 120:00:00\n\n"+\
        f"source /contrib/Tim.Smith/miniconda3/etc/profile.d/conda.sh\n"+\
        f"conda activate ufs2arco\n"+\
        f'python -c "{the_code}"'

    script_dir = "job-scripts"
    fname = f"{script_dir}/submit_1mover{job_id:03d}.sh"

    for this_dir in [slurm_dir, script_dir]:
        if not os.path.isdir(this_dir):
            os.makedirs(this_dir)

    with open(fname, "w") as f:
        f.write(txt)

    subprocess.run(f"sbatch {fname}", shell=True)


if __name__ == "__main__":

    #### STORE CONTAINER
    ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                      storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"},
                      )
    # clip to a few variables to test
    ds = ds[['acond','tmp']]
    # resample
    ds = ds.isel(
        grid_xt=slice(None, None, 4), 
        grid_yt=slice(None, None, 4)
        )
    # update chunks to match 1-deg ds (dont need pfull to be 1)
    ds = ds.chunk({"time":1, 
                   "pfull":127, 
                   "grid_yt":-1, 
                   "grid_xt":-1}
                   )

    dds = xr.Dataset()
    for key, da in ds.data_vars.items():
        
        # loop through vars
        dda = xr.DataArray(
            data=darray.zeros(
                shape=da.shape,
                chunks=da.chunks,
                dtype=da.dtype,
            ),
            dims=da.dims,
            coords=da.coords,
            attrs=da.attrs,
        )
        dds[key] = dda
        
    # store out container
    dds.to_zarr('/Users/mariahpope/Desktop/zarr_testing/v2', 
                compute=False,
                mode='w')
    del dds
    del dda
    print('container done')


    jobs_splits = [int(x) for x in np.linspace(0,87020,15)]
    n_jobs=15
    for job_id in range(n_jobs):
        submit_slurm_mover(job_id)


