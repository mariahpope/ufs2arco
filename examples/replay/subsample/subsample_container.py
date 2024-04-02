import xarray as xr
import numpy as np
import dask.array as darray

path_out = "gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree-subsampled/03h-freq/zarr/"

# open and subsample
ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"},)

ds = ds.isel(grid_xt=slice(None, None, 4), 
             grid_yt=slice(None, None, 4))

# update chunks to match 1-deg ds (pfull needs to be 127)
ds = ds.chunk({"time":1, 
               "pfull":127, 
               "grid_yt":-1, 
               "grid_xt":-1}
               )

# load in so it doesnt cause weird things to happen when we write out
ds['cftime'].load()
ds['ftime'].load()

# start building container
dds = xr.Dataset()
for key, da in ds.data_vars.items():
    print(key)

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
dds.to_zarr(path_out, 
            compute=False,
            mode='w',
            storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"})