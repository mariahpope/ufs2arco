import xarray as xr
import gcsfs
import zarr
import numpy as np
import dask.array as darray

def move_one_job(
        start_timestep,
        end_timestep,
        count,
) -> None:
    ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                    storage_options={"token": "anon"},)
    # clip to a few variables to test
    ds = ds[['acond','tmp']]
    # upsample and clip to timesteps that this job will do
    ds = ds.isel(grid_xt=slice(None, None, 4), 
                 grid_yt=slice(None, None, 4))
    # update chunks to match 1-deg ds (dont need pfull to be 1)
    ds = ds.chunk({"time":1, 
                   "pfull":127, 
                   "grid_yt":-1, 
                   "grid_xt":-1})
    
    splits = [int(x) for x in np.linspace(start_timestep, end_timestep, count)]

    for i in range(len(splits) - 1):

        start_time = splits[i]
        end_time = splits[i + 1]
        
        ds_subset = ds.isel(time=slice(start_time,end_time)).load()
        
        region = {
            "time": slice(start_time, end_time),
            "pfull": slice(None, None),
            "grid_yt": slice(None, None),
            "grid_xt": slice(None, None),
        }
        region = {k : v for k,v in region.items() if k in ds.dims}
        
        ds_subset.to_zarr('/Users/mariahpope/Desktop/zarr_testing/v2',
                        region=region
                        )