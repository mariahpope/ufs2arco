import xarray as xr
import numpy as np
import sys

path_out = "gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree-subsampled/03h-freq/zarr/"

ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"},)

start_timestep = int(sys.argv[1])
end_timestep = int(sys.argv[2]) + 1
timestep_total = end_timestep - start_timestep
timestep_per_loop = 15
groups = int(timestep_total/timestep_per_loop)
splits = [int(x) for x in np.linspace(start_timestep, end_timestep, groups+1)]

for i in range(len(splits) - 1):

    start_time = splits[i]
    end_time = splits[i + 1]
    
    ds_subset = ds.isel(time=slice(start_time,end_time)).load()

    ds_subset = ds_subset.isel(grid_xt=slice(None, None, 4), 
                               grid_yt=slice(None, None, 4))
    
    ds_subset = ds_subset.chunk({"time":1, 
                                 "pfull":127, 
                                 "grid_yt":-1, 
                                 "grid_xt":-1})
    
    ds_subset['ftime'].load()
    ds_subset['cftime'].load()
    
    region = {
        "time": slice(start_time, end_time),
        "pfull": slice(None, None),
        "grid_yt": slice(None, None),
        "grid_xt": slice(None, None),
    }
    region = {k : v for k,v in region.items() if k in ds.dims}
    
    ds_subset.to_zarr(path_out, 
                      region=region,
                      storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"})
    
    del ds_subset