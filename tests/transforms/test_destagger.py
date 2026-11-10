from unittest.mock import MagicMock, patch

import numpy as np
import xarray as xr

from ufs2arco.transforms.destagger import destagger


def _make_staggered_dataset():
    """Dataset with one staggered variable and one regular variable."""
    data_stag = np.arange(2 * 4, dtype=float).reshape(2, 4)
    data_reg = np.arange(2 * 3, dtype=float).reshape(2, 3)
    return xr.Dataset(
        {
            "U": (("south_north", "west_east_stag"), data_stag),
            "T": (("south_north", "west_east"), data_reg),
        }
    )


def test_destagger_applies_to_staggered_variable():
    xds = _make_staggered_dataset()

    # xwrf.destagger averages adjacent points, reducing the stag dim by 1.
    destaggered = xr.DataArray(
        np.arange(2 * 3, dtype=float).reshape(2, 3),
        dims=("south_north", "west_east"),
    )

    with patch("xarray.DataArray.xwrf", create=True) as mock_accessor:
        mock_accessor.destagger.return_value = destaggered
        result = destagger(xds, {"U": "west_east"})

    assert "west_east_stag" not in result["U"].dims
    assert result["U"].dims == ("south_north", "west_east")
    mock_accessor.destagger.assert_called_once()


def test_destagger_skips_when_stag_dim_absent():
    xds = _make_staggered_dataset()

    # T has no staggered dim, so destagger should leave it unchanged.
    result = destagger(xds, {"T": "west_east"})
    assert result["T"].dims == ("south_north", "west_east")
    xr.testing.assert_identical(result["T"], xds["T"])


def test_destagger_drops_unused_stag_dims():
    xds = _make_staggered_dataset()

    destaggered = xr.DataArray(
        np.arange(2 * 3, dtype=float).reshape(2, 3),
        dims=("south_north", "west_east"),
    )

    with patch("xarray.DataArray.xwrf", create=True) as mock_accessor:
        mock_accessor.destagger.return_value = destaggered
        result = destagger(xds, {"U": "west_east"})

    # After destaggering U, the staggered dim is no longer used and dropped.
    assert "west_east_stag" not in result.dims


def test_destagger_returns_dataset():
    xds = _make_staggered_dataset()
    result = destagger(xds, {})
    assert isinstance(result, xr.Dataset)
    # No config means no changes and no unused dims to drop.
    assert set(result.data_vars) == {"U", "T"}
