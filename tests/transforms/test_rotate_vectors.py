import numpy as np
import pytest
import xarray as xr

from ufs2arco.transforms.rotate_vectors import rotate_lambert_conical_vectors


def _attrs():
    return {
        "GRIB_gridType": "lambert",
        "GRIB_uvRelativeToGrid": 1,
        "GRIB_latitudeOfFirstGridPointInDegrees": 25.0,
        "GRIB_longitudeOfFirstGridPointInDegrees": 260.0,
        "GRIB_Latin1InDegrees": 25.0,
        "GRIB_Latin2InDegrees": 25.0,
        "GRIB_LoVInDegrees": 262.5,
    }


def test_rotate_vectors_raises_when_required_attrs_missing():
    u = xr.DataArray(np.ones((2, 2)), dims=("y", "x"), coords={"longitude": ("x", [0.0, 1.0])}, name="u")
    v = xr.DataArray(np.ones((2, 2)), dims=("y", "x"), coords={"longitude": ("x", [0.0, 1.0])}, name="v")
    with pytest.raises(AttributeError):
        rotate_lambert_conical_vectors(u, v)


def test_rotate_vectors_sets_grid_relative_flag_to_zero():
    u = xr.DataArray(
        np.ones((2, 2)),
        dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])},
        name="u",
        attrs=_attrs(),
    )
    v = xr.DataArray(
        np.ones((2, 2)),
        dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])},
        name="v",
        attrs=_attrs(),
    )
    ue, vn = rotate_lambert_conical_vectors(u, v)
    assert ue.attrs["GRIB_uvRelativeToGrid"] == 0
    assert vn.attrs["GRIB_uvRelativeToGrid"] == 0


def test_rotate_vectors_wrapper_processes_pairs():
    from ufs2arco.transforms.rotate_vectors import rotate_vectors

    u = xr.DataArray(
        np.ones((2, 2)), dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])}, name="u", attrs=_attrs(),
    )
    v = xr.DataArray(
        np.ones((2, 2)), dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])}, name="v", attrs=_attrs(),
    )
    xds = xr.Dataset({"u": u, "v": v})
    out = rotate_vectors(xds, vector_pairs=[["u", "v"]])
    assert out["u"].attrs["GRIB_uvRelativeToGrid"] == 0
    assert out["v"].attrs["GRIB_uvRelativeToGrid"] == 0


def test_rotate_vectors_differing_latins_uses_log_branch():
    attrs = _attrs()
    attrs["GRIB_Latin1InDegrees"] = 25.0
    attrs["GRIB_Latin2InDegrees"] = 40.0  # differs from Latin1 -> log-based angle
    u = xr.DataArray(
        np.ones((2, 2)), dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])}, name="u", attrs=attrs,
    )
    v = xr.DataArray(
        np.ones((2, 2)), dims=("y", "x"),
        coords={"longitude": ("x", [0.0, 1.0])}, name="v", attrs=attrs,
    )
    ue, vn = rotate_lambert_conical_vectors(u, v)
    assert np.isfinite(ue.values).all()
    assert np.isfinite(vn.values).all()
