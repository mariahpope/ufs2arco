import xarray as xr

ds = xr.open_zarr("gcs://noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr",
                  storage_options={"token": "anon"},)

ds = ds.isel(time=slice(1,2)).load()

print(ds)

print(ds.nbytes)


