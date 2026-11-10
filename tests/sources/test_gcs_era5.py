from unittest.mock import patch

import pandas as pd

from ufs2arco.sources.gcs_era5 import GCSERA5


def test_class_attributes():
    assert GCSERA5.sample_dims == ("time",)
    assert GCSERA5.horizontal_dims == ("latitude", "longitude")
    assert GCSERA5.static_vars == ("land_sea_mask", "geopotential_at_surface")


def test_init_sets_time():
    time = {"start": "2020-01-01T00", "end": "2020-01-01T06", "freq": "6h"}
    with patch("ufs2arco.sources.gcs_era5.CloudZarrData.__init__", return_value=None):
        source = GCSERA5(time=time, uri="gcs://dummy.zarr")

    assert source.time.equals(pd.date_range(**time))


def test_init_forwards_kwargs_to_super():
    time = {"start": "2020-01-01T00", "end": "2020-01-01T06", "freq": "6h"}
    uri = "gcs://dummy.zarr"

    with patch(
        "ufs2arco.sources.gcs_era5.CloudZarrData.__init__", return_value=None
    ) as mock_super_init:
        GCSERA5(
            time=time,
            uri=uri,
            variables=["t"],
            levels=[500],
            use_nearest_levels=True,
            slices={"time": slice(0, 1)},
        )

    mock_super_init.assert_called_once()
    _, kwargs = mock_super_init.call_args
    assert kwargs["uri"] == uri
    assert kwargs["variables"] == ["t"]
    assert kwargs["levels"] == [500]
    assert kwargs["use_nearest_levels"] is True
    assert kwargs["slices"] == {"time": slice(0, 1)}
    # GCSERA5 does not pass storage_options to the parent.
    assert "storage_options" not in kwargs


def test_init_default_kwargs_to_super():
    time = {"start": "2020-01-01T00", "end": "2020-01-01T06", "freq": "6h"}

    with patch(
        "ufs2arco.sources.gcs_era5.CloudZarrData.__init__", return_value=None
    ) as mock_super_init:
        GCSERA5(time=time, uri="gcs://dummy.zarr")

    _, kwargs = mock_super_init.call_args
    assert kwargs["variables"] is None
    assert kwargs["levels"] is None
    assert kwargs["use_nearest_levels"] is False
    assert kwargs["slices"] is None
