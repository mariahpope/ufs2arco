import numpy as np
import pandas as pd
import pytest
import xarray as xr

import ufs2arco.sources.cloud_zarr as cmod
from ufs2arco.sources.cloud_zarr import CloudZarrData


class _CloudLike(CloudZarrData):
    sample_dims = ("time",)
    horizontal_dims = ("latitude", "longitude")
    static_vars = ("lsm",)
    time = pd.date_range("2020-01-01", periods=2, freq="6h")

    @property
    def rename(self):
        return {}


def _cloud_ds():
    return xr.Dataset(
        {
            "lsm": (("time", "latitude", "longitude"), np.ones((2, 2, 2))),
            "t2m": (("time", "latitude", "longitude"), np.ones((2, 2, 2)) * 2),
        },
        coords={
            "time": pd.date_range("2020-01-01", periods=2, freq="6h"),
            "latitude": [0.0, 1.0],
            "longitude": [10.0, 11.0],
        },
    )


def _level_ds():
    return xr.Dataset(
        {
            "t": (("time", "level", "latitude", "longitude"), np.ones((2, 3, 2, 2))),
            "w": (("time", "level_stag", "latitude", "longitude"), np.ones((2, 4, 2, 2))),
            "lsm": (("time", "latitude", "longitude"), np.ones((2, 2, 2))),
        },
        coords={
            "time": pd.date_range("2020-01-01", periods=2, freq="6h"),
            "level": ("level", [100, 500, 1000]),
            "level_stag": ("level_stag", [100, 500, 1000, 1001]),
            "latitude": [0.0, 1.0],
            "longitude": [10.0, 11.0],
        },
    )


@pytest.fixture
def patch_cloud(monkeypatch):
    monkeypatch.setattr(cmod.xr, "open_zarr", lambda *a, **k: _cloud_ds())


@pytest.fixture
def patch_level(monkeypatch):
    monkeypatch.setattr(cmod.xr, "open_zarr", lambda *a, **k: _level_ds())


# --- open_sample_dataset ---

@pytest.mark.parametrize(
    "idx, open_static, expect_static",
    [
        (1, False, False),  # later sample, static excluded
        (1, True, True),    # later sample, static requested
        (0, False, True),   # first sample, static always included
    ],
)
def test_open_sample_dataset_static(patch_cloud, idx, open_static, expect_static):
    src = _CloudLike(uri="s3://dummy", variables=["lsm", "t2m"])
    out = src.open_sample_dataset(
        {"time": src._xds.time.values[idx]}, open_static_vars=open_static
    )
    assert "t2m" in out
    assert ("lsm" in out) is expect_static


# --- available_* properties ---

def test_available_variables(patch_cloud):
    src = _CloudLike(uri="s3://dummy", variables=["lsm", "t2m"])
    assert set(src.available_variables) == {"lsm", "t2m"}


def test_available_levels(patch_level):
    src = _CloudLike(uri="s3://dummy", variables=["t"])
    assert src.available_levels == (100, 500, 1000)


def test_available_stag_levels(patch_level):
    src = _CloudLike(uri="s3://dummy", variables=["w"])
    assert src.available_stag_levels == (100, 500, 1000, 1001)


# --- level selection ---

def test_level_selection(patch_level):
    src = _CloudLike(uri="s3://dummy", variables=["t"], levels=[500])
    assert src._xds["level"].values.tolist() == [500]


def test_stag_level_selection_appends_extra_level(patch_level):
    src = _CloudLike(uri="s3://dummy", variables=["w"], levels=[500, 1000])
    assert src._xds["level_stag"].values.tolist() == [500, 1000, 1001]


def test_use_nearest_levels(patch_level):
    src = _CloudLike(
        uri="s3://dummy", variables=["t"], levels=[400], use_nearest_levels=True
    )
    assert src._xds["level"].values.tolist() == [500]


# --- slices ---

def test_apply_isel_slices(patch_level):
    src = _CloudLike(
        uri="s3://dummy", variables=["t"], slices={"isel": {"longitude": [0, 1]}}
    )
    assert src._xds["longitude"].values.tolist() == [10.0]
