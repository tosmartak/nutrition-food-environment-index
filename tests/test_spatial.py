import numpy as np
import pandas as pd
import pytest

from nfei.spatial import (
    calc_distance,
    features_proximity_agg,
    haversine_vectorized,
)


def vendor_points():
    return pd.DataFrame(
        {
            "vendor_id": [1, 2, 3],
            "_longitude": [36.8000, 36.8002, 36.9000],
            "_latitude": [-1.3000, -1.3002, -1.4000],
            "shop": [1, 1, 0],
            "kiosk": [0, 1, 1],
            "mlds": [4, 8, 10],
        }
    )


def focal_points():
    return pd.DataFrame(
        {
            "hh_id": [1, 2],
            "_longitude": [36.8001, 37.2000],
            "_latitude": [-1.3001, -1.7000],
        }
    )


def test_haversine_vectorized_returns_zero_for_same_point():
    result = haversine_vectorized(36.8, -1.3, 36.8, -1.3)
    assert result == pytest.approx(0)


def test_calc_distance_returns_nearest_distance_and_closest_column():
    households = focal_points()
    vendors = vendor_points()

    result = calc_distance(
        households,
        vendors,
        include_col="vendor_id",
    )

    assert "distance_km" in result.columns
    assert "closest_vendor_id" in result.columns
    assert result["closest_vendor_id"].iloc[0] in [1, 2]
    assert result["distance_km"].iloc[0] < 0.05


def test_calc_distance_custom_column_names():
    df1 = pd.DataFrame({"lon": [36.8], "lat": [-1.3]})
    df2 = pd.DataFrame({"x": [36.8001], "y": [-1.3001]})

    result = calc_distance(
        df1,
        df2,
        data1_lon="lon",
        data1_lat="lat",
        data2_lon="x",
        data2_lat="y",
        col_title="nearest_vendor_km",
    )

    assert "nearest_vendor_km" in result.columns
    assert result["nearest_vendor_km"].iloc[0] < 0.05


def test_calc_distance_raises_error_when_data2_empty():
    df1 = pd.DataFrame({"_longitude": [36.8], "_latitude": [-1.3]})
    df2 = pd.DataFrame(columns=["_longitude", "_latitude"])

    with pytest.raises(ValueError):
        calc_distance(df1, df2)


def test_features_proximity_agg_count_between_two_dataframes():
    result = features_proximity_agg(
        focal_points(),
        vendor_points(),
        buffer=100,
        method="count",
        overall_title="vendors_within_100m",
    )

    assert result["vendors_within_100m"].tolist() == [2, 0]


def test_features_proximity_agg_sum_between_two_dataframes():
    result = features_proximity_agg(
        focal_points().iloc[[0]],
        vendor_points(),
        buffer=100,
        col_to_agg=["shop", "kiosk"],
        method="sum",
        include_sum=True,
        overall_title="retail_diversity",
    )

    assert result["shop_within_100m"].iloc[0] == 2
    assert result["kiosk_within_100m"].iloc[0] == 1
    assert result["retail_diversity"].iloc[0] == 3


def test_features_proximity_agg_mean_between_two_dataframes():
    result = features_proximity_agg(
        focal_points().iloc[[0]],
        vendor_points(),
        buffer=100,
        col_to_agg=["mlds"],
        method="mean",
    )

    assert result["mlds_within_100m"].iloc[0] == 6


def test_features_proximity_agg_max_between_two_dataframes():
    result = features_proximity_agg(
        focal_points().iloc[[0]],
        vendor_points(),
        buffer=100,
        col_to_agg=["mlds"],
        method="max",
    )

    assert result["mlds_within_100m"].iloc[0] == 8


def test_features_proximity_agg_self_count_false_excludes_self_for_count():
    df = vendor_points().iloc[:2].copy()

    result = features_proximity_agg(
        df,
        df,
        buffer=100,
        method="count",
        self_count=False,
        overall_title="nearby_vendors",
    )

    assert result["nearby_vendors"].tolist() == [1, 1]


def test_features_proximity_agg_self_count_true_includes_self_for_count():
    df = vendor_points().iloc[:2].copy()

    result = features_proximity_agg(
        df,
        df,
        buffer=100,
        method="count",
        self_count=True,
        overall_title="nearby_vendors",
    )

    assert result["nearby_vendors"].tolist() == [2, 2]


def test_features_proximity_agg_self_count_false_excludes_self_before_mean():
    df = vendor_points().iloc[:2].copy()

    result = features_proximity_agg(
        df,
        df,
        buffer=100,
        col_to_agg=["mlds"],
        method="mean",
        self_count=False,
    )

    assert result["mlds_within_100m"].tolist() == [8, 4]


def test_features_proximity_agg_drop_col_to_agg_keeps_only_overall():
    result = features_proximity_agg(
        focal_points().iloc[[0]],
        vendor_points(),
        buffer=100,
        col_to_agg=["shop", "kiosk"],
        method="sum",
        include_sum=True,
        overall_title="retail_diversity",
        drop_col_to_agg=True,
    )

    assert "retail_diversity" in result.columns
    assert "shop_within_100m" not in result.columns
    assert "kiosk_within_100m" not in result.columns
    assert result["retail_diversity"].iloc[0] == 3


def test_features_proximity_agg_raises_error_for_invalid_method():
    with pytest.raises(ValueError):
        features_proximity_agg(
            focal_points(),
            vendor_points(),
            buffer=100,
            method="median",
        )


def test_features_proximity_agg_raises_error_for_missing_col_to_agg():
    with pytest.raises(ValueError):
        features_proximity_agg(
            focal_points(),
            vendor_points(),
            buffer=100,
            method="sum",
        )


def test_features_proximity_agg_raises_error_for_missing_aggregation_column():
    with pytest.raises(KeyError):
        features_proximity_agg(
            focal_points(),
            vendor_points(),
            buffer=100,
            col_to_agg=["missing_col"],
            method="sum",
        )


def test_features_proximity_agg_raises_error_for_invalid_buffer():
    with pytest.raises(ValueError):
        features_proximity_agg(
            focal_points(),
            vendor_points(),
            buffer=0,
            method="count",
        )