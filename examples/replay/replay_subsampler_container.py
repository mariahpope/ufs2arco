import xarray as xr
#import gcsfs
#import zarr
import numpy as np
import dask.array as darray

path_out = "gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree-subsampled/03h-freq/zarr/"
#coords_path_out = "gcs://noaa-ufs-gefsv13replay/ufs-hr1/1.00-degree/coordinates/zarr/"

#### STORE CONTAINER
ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                storage_options={"token": "/contrib/Mariah.Pope/.gcs/replay-service-account.json"},)
# clip to a few variables to test
#ds = ds[['acond','tmp']]
# upsample
ds = ds.isel(grid_xt=slice(None, None, 4), 
             grid_yt=slice(None, None, 4))
# update chunks to match 1-deg ds (dont need pfull to be 1)
ds = ds.chunk({"time":1, 
               "pfull":127, 
               "grid_yt":-1, 
               "grid_xt":-1})

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
del dds
del dda
print('container done')