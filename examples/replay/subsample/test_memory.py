import xarray as xr
import sys

ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                  storage_options={"token": "anon"},)
ds = ds.isel(time=slice(1,2), 
             grid_xt=slice(None, None, 4), 
             grid_yt=slice(None, None, 4)).load()
print(ds)

print(ds.nbytes)


