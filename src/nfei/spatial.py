from __future__ import annotations

import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import Transformer


def haversine_vectorized(lon1, lat1, lon2, lat2) -> np.ndarray:
    """
    Calculate great-circle distances between coordinate pairs using Haversine.

    Returns distances in kilometers.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    earth_radius_km = 6371

    return c * earth_radius_km


def calc_distance(
    data1: pd.DataFrame,
    data2: pd.DataFrame,
    include_col: str | None = None,
    col_title: str = "distance_km",
    data1_lon: str = "_longitude",
    data1_lat: str = "_latitude",
    data2_lon: str = "_longitude",
    data2_lat: str = "_latitude",
) -> pd.DataFrame:
    """
    Calculate nearest distance from each observation in data1 to observations in data2.

    This mirrors the original NFEI notebook logic. For each row in data1, the
    function calculates the Haversine distance to all rows in data2 and keeps
    the closest distance.

    Parameters
    ----------
    data1:
        Primary dataframe. Each row receives the nearest distance to data2.

    data2:
        Secondary dataframe containing candidate destination points.

    include_col:
        Optional column from data2 to bring back from the nearest observation.
        For example, if include_col='vendor_type', the returned dataframe gets
        a column named 'closest_vendor_type'.

    col_title:
        Name of the distance column to add. Distances are in kilometers.

    data1_lon, data1_lat:
        Longitude and latitude column names in data1.

    data2_lon, data2_lat:
        Longitude and latitude column names in data2.

    Returns
    -------
    pd.DataFrame
        Copy of data1 with a nearest-distance column. If include_col is given,
        a closest_{include_col} column is also added.

    Notes
    -----
    This function uses latitude and longitude directly through the Haversine
    formula. It is appropriate for nearest-distance calculation in kilometers
    without requiring users to convert dataframes to GeoDataFrames.
    """
    required_data1_cols = [data1_lon, data1_lat]
    required_data2_cols = [data2_lon, data2_lat]

    if include_col is not None:
        required_data2_cols.append(include_col)

    missing_data1 = [col for col in required_data1_cols if col not in data1.columns]
    missing_data2 = [col for col in required_data2_cols if col not in data2.columns]

    if missing_data1:
        raise KeyError(f"Missing required column(s) in data1: {missing_data1}")

    if missing_data2:
        raise KeyError(f"Missing required column(s) in data2: {missing_data2}")

    if data2.empty:
        raise ValueError("data2 must contain at least one observation.")

    df1 = data1.copy()
    df2 = data2.copy().reset_index(drop=True)

    distances = []
    closest_values = []

    for _, row in df1.iterrows():
        point_distances = haversine_vectorized(
            row[data1_lon],
            row[data1_lat],
            df2[data2_lon].to_numpy(),
            df2[data2_lat].to_numpy(),
        )

        min_index = int(np.argmin(point_distances))
        distances.append(float(point_distances[min_index]))

        if include_col is not None:
            closest_values.append(df2.iloc[min_index][include_col])

    df1[col_title] = distances

    if include_col is not None:
        df1[f"closest_{include_col}"] = closest_values

    return df1

def _estimate_utm_crs_from_lonlat(
    df: pd.DataFrame,
    lon_col: str,
    lat_col: str,
) -> str:
    """
    Estimate a UTM CRS from longitude and latitude columns.

    This avoids relying on GeoPandas estimate_utm_crs(), which may trigger
    upstream PyProj or NumPy deprecation warnings in some environments.
    """
    lon = float(df[lon_col].mean())
    lat = float(df[lat_col].mean())

    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone

    return f"EPSG:{epsg}"

def _to_projected_gdf(
    df: pd.DataFrame,
    lon_col: str,
    lat_col: str,
    input_crs: str | int = "EPSG:4326",
    projected_crs: str | int | None = None,
) -> gpd.GeoDataFrame:
    """
    Convert a pandas dataframe with coordinate columns to a projected GeoDataFrame.

    Coordinates are transformed directly with PyProj rather than using
    GeoDataFrame.to_crs(). This avoids known upstream deprecation warnings that
    can occur with single-row GeoDataFrames in some NumPy/PyProj combinations.
    """
    missing_cols = [col for col in [lon_col, lat_col] if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing coordinate column(s): {missing_cols}")

    if projected_crs is None:
        projected_crs = _estimate_utm_crs_from_lonlat(
            df=df,
            lon_col=lon_col,
            lat_col=lat_col,
        )

    transformer = Transformer.from_crs(
        input_crs,
        projected_crs,
        always_xy=True,
    )

    projected_points = [
        transformer.transform(float(lon), float(lat))
        for lon, lat in zip(df[lon_col], df[lat_col], strict=False)
    ]

    x_coords = [point[0] for point in projected_points]
    y_coords = [point[1] for point in projected_points]

    return gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(x_coords, y_coords),
        crs=projected_crs,
    )


def features_proximity_agg(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    buffer: float,
    col_to_agg: list[str] | None = None,
    self_count: bool = False,
    include_sum: bool = False,
    method: str = "sum",
    df1_lat: str = "_latitude",
    df1_lon: str = "_longitude",
    df2_lat: str = "_latitude",
    df2_lon: str = "_longitude",
    overall_title: str = "Overall_aggregate",
    drop_col_to_agg: bool = False,
    input_crs: str | int = "EPSG:4326",
    projected_crs: str | int | None = None,
) -> pd.DataFrame:
    """
    Aggregate features from df2 within a buffer around each observation in df1.

    This is a cleaned version of the original NFEI notebook function. It accepts
    ordinary pandas DataFrames with latitude and longitude columns, converts them
    internally to GeoDataFrames, creates buffers around df1 points, and aggregates
    nearby df2 observations within each buffer.

    Parameters
    ----------
    df1:
        Primary dataframe. A buffer is created around each row.

    df2:
        Secondary dataframe. Rows falling within each df1 buffer are aggregated.

    buffer:
        Buffer radius in meters.

    col_to_agg:
        Columns in df2 to aggregate. Required for 'sum', 'mean', and 'max'.
        Not required for 'count'.

    self_count:
        If False and df1 and df2 are the same object, each row is excluded from
        its own buffer before aggregation. This is done before aggregation, which
        is more appropriate than subtracting after aggregation.

    include_sum:
        If True and method is not 'count', adds an overall aggregate column by
        summing the aggregated columns row-wise.

    method:
        Aggregation method. One of: 'sum', 'mean', 'max', 'count'.

    df1_lat, df1_lon:
        Latitude and longitude column names in df1.

    df2_lat, df2_lon:
        Latitude and longitude column names in df2.

    overall_title:
        Name of the count column for method='count', or the overall aggregate
        column when include_sum=True.

    drop_col_to_agg:
        If True, drops individual aggregated columns and keeps only the overall
        aggregate. Only valid when include_sum=True and method is not 'count'.

    input_crs:
        CRS of the input coordinates. Default is EPSG:4326.

    projected_crs:
        Projected CRS used for distance and buffer operations. If None, a local
        UTM CRS is estimated automatically.

    Returns
    -------
    pd.DataFrame
        Copy of df1 with buffer-based aggregate features added.
    """
    if buffer <= 0:
        raise ValueError("buffer must be greater than zero.")

    valid_methods = {"sum", "mean", "max", "count"}
    if method not in valid_methods:
        raise ValueError(f"method must be one of {sorted(valid_methods)}.")

    if col_to_agg is None:
        col_to_agg = []

    if method != "count" and len(col_to_agg) == 0:
        raise ValueError("col_to_agg must be provided when method is not 'count'.")

    missing_agg_cols = [col for col in col_to_agg if col not in df2.columns]
    if missing_agg_cols:
        raise KeyError(f"Column(s) in col_to_agg not found in df2: {missing_agg_cols}")

    if drop_col_to_agg and method != "count" and not include_sum:
        raise ValueError(
            "drop_col_to_agg=True requires include_sum=True when method is not 'count'."
        )

    same_object = df1 is df2

    data1 = df1.copy().reset_index(drop=True)
    data1["ID"] = data1.index

    data2 = df2.copy().reset_index(drop=True)
    data2["TARGET_ID"] = data2.index

    gdf1 = _to_projected_gdf(
        data1,
        lon_col=df1_lon,
        lat_col=df1_lat,
        input_crs=input_crs,
        projected_crs=projected_crs,
    )

    gdf2 = _to_projected_gdf(
        data2,
        lon_col=df2_lon,
        lat_col=df2_lat,
        input_crs=input_crs,
        projected_crs=gdf1.crs,
    )

    gdf1["buffer_m"] = gdf1.geometry.buffer(buffer)

    joined = gpd.sjoin(
        gdf1.set_geometry("buffer_m"),
        gdf2,
        how="left",
        predicate="intersects",
    )

    if same_object and not self_count:
        joined = joined[joined["ID"] != joined["TARGET_ID"]]

    if method == "count":
        matched = joined[joined["index_right"].notna()]
        summary = matched.groupby("ID").size().reset_index(name=overall_title)

    else:
        agg_cols = []

        for col in col_to_agg:
            right_col = f"{col}_right"
            agg_cols.append(right_col if right_col in joined.columns else col)

        if method == "sum":
            summary = joined.groupby("ID")[agg_cols].sum().reset_index()
        elif method == "mean":
            summary = joined.groupby("ID")[agg_cols].mean().reset_index()
        else:
            summary = joined.groupby("ID")[agg_cols].max().reset_index()

        buffer_text = f"_within_{int(buffer)}m"

        rename_map = {
            col: col.replace("_right", buffer_text)
            if col.endswith("_right")
            else f"{col}{buffer_text}"
            for col in agg_cols
        }

        summary = summary.rename(columns=rename_map)
        renamed_agg_cols = list(rename_map.values())

        if include_sum:
            summary[overall_title] = summary[renamed_agg_cols].sum(axis=1)

        if drop_col_to_agg:
            summary = summary.drop(columns=renamed_agg_cols)

    result = gdf1.merge(summary, on="ID", how="left")
    result = result.drop(columns=["ID", "buffer_m", "geometry"])

    added_cols = [col for col in result.columns if col not in df1.columns]
    result[added_cols] = result[added_cols].fillna(0)

    return pd.DataFrame(result)