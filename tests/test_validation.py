import numpy as np
import pandas as pd
import pytest

from nfei.validation import fix_spatial_outliers, mad_based_outlier


def test_mad_based_outlier_detects_extreme_value_in_series():
    values = pd.Series([10, 11, 12, 13, 100])

    result = mad_based_outlier(values, threshold=3.0)

    assert result.tolist() == [False, False, False, False, True]


def test_mad_based_outlier_accepts_numpy_array():
    values = np.array([10, 11, 12, 13, 100])

    result = mad_based_outlier(values, threshold=3.0)

    assert result.tolist() == [False, False, False, False, True]


def test_mad_based_outlier_returns_false_when_mad_is_zero():
    values = pd.Series([5, 5, 5, 5])

    result = mad_based_outlier(values)

    assert result.tolist() == [False, False, False, False]


def test_mad_based_outlier_raises_error_for_empty_values():
    with pytest.raises(ValueError):
        mad_based_outlier(pd.Series(dtype=float))


def test_mad_based_outlier_raises_error_for_non_numeric_values():
    values = pd.Series(["a", "b", "c"])

    with pytest.raises(TypeError):
        mad_based_outlier(values)


def test_fix_spatial_outliers_corrects_longitude_outlier():
    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 100.00],
            "_latitude": [-1.30, -1.31, -1.32, -1.33],
        }
    )

    result = fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=False,
        return_outlier_flag=True,
    )

    assert result["spatial_outlier"].tolist() == [False, False, False, True]
    assert result["_longitude"].iloc[-1] == pytest.approx(
        df["_longitude"].iloc[:3].median()
    )
    assert result["_latitude"].iloc[-1] == pytest.approx(
        df["_latitude"].iloc[:3].median()
    )


def test_fix_spatial_outliers_corrects_latitude_outlier():
    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 36.83],
            "_latitude": [-1.30, -1.31, -1.32, -50.00],
        }
    )

    result = fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=False,
        return_outlier_flag=True,
    )

    assert result["spatial_outlier"].tolist() == [False, False, False, True]
    assert result["_longitude"].iloc[-1] == pytest.approx(
        df["_longitude"].iloc[:3].median()
    )
    assert result["_latitude"].iloc[-1] == pytest.approx(
        df["_latitude"].iloc[:3].median()
    )


def test_fix_spatial_outliers_does_not_modify_original_dataframe():
    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 100.00],
            "_latitude": [-1.30, -1.31, -1.32, -1.33],
        }
    )

    original = df.copy()

    fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=False,
    )

    pd.testing.assert_frame_equal(df, original)


def test_fix_spatial_outliers_custom_outlier_column_name():
    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 100.00],
            "_latitude": [-1.30, -1.31, -1.32, -1.33],
        }
    )

    result = fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=False,
        return_outlier_flag=True,
        outlier_col="coord_outlier",
    )

    assert "coord_outlier" in result.columns
    assert "spatial_outlier" not in result.columns


def test_fix_spatial_outliers_without_flag_column():
    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 100.00],
            "_latitude": [-1.30, -1.31, -1.32, -1.33],
        }
    )

    result = fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=False,
        return_outlier_flag=False,
    )

    assert "spatial_outlier" not in result.columns


def test_fix_spatial_outliers_raises_error_for_missing_coordinate_column():
    df = pd.DataFrame({"_longitude": [36.8, 36.9]})

    with pytest.raises(KeyError):
        fix_spatial_outliers(
            df,
            latitude="_latitude",
            longitude="_longitude",
            show_plots=False,
        )


def test_fix_spatial_outliers_raises_error_for_non_numeric_latitude():
    df = pd.DataFrame(
        {
            "_longitude": [36.8, 36.9],
            "_latitude": ["bad", "data"],
        }
    )

    with pytest.raises(TypeError):
        fix_spatial_outliers(
            df,
            latitude="_latitude",
            longitude="_longitude",
            show_plots=False,
        )


def test_fix_spatial_outliers_raises_error_for_non_numeric_longitude():
    df = pd.DataFrame(
        {
            "_longitude": ["bad", "data"],
            "_latitude": [-1.3, -1.4],
        }
    )

    with pytest.raises(TypeError):
        fix_spatial_outliers(
            df,
            latitude="_latitude",
            longitude="_longitude",
            show_plots=False,
        )


def test_fix_spatial_outliers_show_plots_runs_without_error(monkeypatch):
    import matplotlib.pyplot as plt

    df = pd.DataFrame(
        {
            "_longitude": [36.80, 36.81, 36.82, 100.00],
            "_latitude": [-1.30, -1.31, -1.32, -1.33],
        }
    )

    monkeypatch.setattr(plt, "show", lambda: None)

    result = fix_spatial_outliers(
        df,
        latitude="_latitude",
        longitude="_longitude",
        show_plots=True,
    )

    assert isinstance(result, pd.DataFrame)