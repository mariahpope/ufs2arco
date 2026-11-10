import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture
def conus404_cls():
    """Import the CONUS404 class with external STAC/planetary_computer deps mocked.

    The class connects to a remote STAC catalog at class-definition time, so we
    patch those modules before importing the module under test.
    """
    mock_storage_options = {"account_name": "test"}

    mock_asset = MagicMock()
    mock_asset.extra_fields = {"xarray:storage_options": mock_storage_options}

    mock_collection = MagicMock()
    mock_collection.assets = {"zarr-abfs": mock_asset}

    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection

    mock_pystac_client = MagicMock()
    mock_pystac_client.Client.open.return_value = mock_client

    mock_planetary_computer = MagicMock()

    with patch.dict(
        sys.modules,
        {
            "pystac_client": mock_pystac_client,
            "planetary_computer": mock_planetary_computer,
        },
    ):
        # Ensure a fresh import so the mocked modules are picked up.
        sys.modules.pop("ufs2arco.sources.conus404", None)
        from ufs2arco.sources.conus404 import CONUS404

        yield CONUS404, mock_storage_options

    sys.modules.pop("ufs2arco.sources.conus404", None)


def test_class_attributes(conus404_cls):
    CONUS404, _ = conus404_cls
    assert CONUS404.sample_dims == ("time",)
    assert CONUS404.horizontal_dims == ("latitude", "longitude")


def test_storage_options_from_asset(conus404_cls):
    CONUS404, mock_storage_options = conus404_cls
    assert CONUS404.storage_options == mock_storage_options


def test_available_levels(conus404_cls):
    CONUS404, _ = conus404_cls
    obj = CONUS404.__new__(CONUS404)
    levels = obj.available_levels
    assert levels == tuple(range(50))
    assert len(levels) == 50


def test_available_stag_levels(conus404_cls):
    CONUS404, _ = conus404_cls
    obj = CONUS404.__new__(CONUS404)
    stag_levels = obj.available_stag_levels
    assert stag_levels == tuple(range(51))
    assert len(stag_levels) == 51


def test_rename_mapping(conus404_cls):
    CONUS404, _ = conus404_cls
    obj = CONUS404.__new__(CONUS404)
    assert obj.rename == {
        "bottom_top": "level",
        "bottom_top_stag": "level_stag",
        "south_north": "latitude",
        "west_east": "longitude",
        "south_north_stag": "latitude_stag",
        "west_east_stag": "longitude_stag",
    }


def test_init_sets_time_and_calls_super(conus404_cls):
    CONUS404, mock_storage_options = conus404_cls

    time = {"start": "2000-01-01", "end": "2000-01-02", "freq": "1h"}
    uri = "abfs://test/conus404.zarr"

    with patch(
        "ufs2arco.sources.conus404.CloudZarrData.__init__", return_value=None
    ) as mock_super_init:
        obj = CONUS404(time=time, uri=uri)

    expected_time = pd.date_range(**time)
    assert obj.time.equals(expected_time)

    mock_super_init.assert_called_once()
    _, kwargs = mock_super_init.call_args
    assert kwargs["uri"] == uri
    assert kwargs["variables"] is None
    assert kwargs["levels"] is None
    assert kwargs["use_nearest_levels"] is False
    assert kwargs["slices"] is None
    assert kwargs["storage_options"] == mock_storage_options
