from __future__ import annotations

import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import Transformer


def haversine_vectorized(lon1, lat1, lon2, lat2) -> np.ndarray:
    """
    Calculate great-circle distances using the Haversine formula.

    This function computes the distance between longitude and latitude
    coordinates using the Haversine formula. It is used in the NFEI spatial
    workflow for direct distance calculations on geographic coordinates without
    requiring users to first convert their data into GeoDataFrames.

    Distances are returned in kilometres.

    Parameters
    ----------
    lon1:
        Longitude of the first point or points, in decimal degrees.

    lat1:
        Latitude of the first point or points, in decimal degrees.

    lon2:
        Longitude of the second point or points, in decimal degrees.

    lat2:
        Latitude of the second point or points, in decimal degrees.

    Returns
    -------
    np.ndarray
        Great-circle distance or distances in kilometres.

    Notes
    -----
    Input coordinates must be in decimal degrees. The function internally
    converts coordinates to radians before applying the Haversine formula.

    This function is most useful for direct point-to-point or one-to-many
    distance calculations. For buffer-based exposure indicators, use
    :func:`features_proximity_agg`.

    Examples
    --------
    Calculate the distance between two points:

    >>> import nfei
    >>>
    >>> distance = nfei.haversine_vectorized(
    ...     lon1=36.8000,
    ...     lat1=-1.3000,
    ...     lon2=36.8002,
    ...     lat2=-1.3002,
    ... )

    Calculate distances from one point to several candidate points:

    >>> import numpy as np
    >>> distances = nfei.haversine_vectorized(
    ...     lon1=36.8000,
    ...     lat1=-1.3000,
    ...     lon2=np.array([36.8002, 36.9000]),
    ...     lat2=np.array([-1.3002, -1.4000]),
    ... )
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
    Calculate nearest distance between two sets of observations.

    This function calculates the nearest distance from each observation in
    ``data1`` to observations in ``data2`` using longitude and latitude
    coordinates. It supports NFEI workflows where users need to measure proximity
    between food environment features, such as households and vendors, vendors
    and water points, or vendors and sanitation facilities.

    For each row in ``data1``, the function computes the Haversine distance to
    all rows in ``data2`` and keeps the closest distance.

    Parameters
    ----------
    data1:
        Primary dataframe. Each row receives the nearest distance to
        observations in ``data2``.

    data2:
        Secondary dataframe containing candidate destination points.

    include_col:
        Optional column from ``data2`` to bring back from the nearest
        observation. For example, if ``include_col="vendor_type"``, the returned
        dataframe receives a column named ``"closest_vendor_type"``.

    col_title:
        Name of the distance column to add. Distances are returned in
        kilometres. The default is ``"distance_km"``.

    data1_lon:
        Longitude column name in ``data1``. The default is ``"_longitude"``.

    data1_lat:
        Latitude column name in ``data1``. The default is ``"_latitude"``.

    data2_lon:
        Longitude column name in ``data2``. The default is ``"_longitude"``.

    data2_lat:
        Latitude column name in ``data2``. The default is ``"_latitude"``.

    Returns
    -------
    pd.DataFrame
        Copy of ``data1`` with a nearest-distance column added. If
        ``include_col`` is provided, a ``"closest_{include_col}"`` column is
        also added.

    Raises
    ------
    KeyError
        If required longitude or latitude columns are missing from either
        dataframe, or if ``include_col`` is provided but not found in ``data2``.

    ValueError
        If ``data2`` contains no observations.

    Notes
    -----
    This function uses geographic coordinates directly through the Haversine
    formula and returns distances in kilometres.

    It is appropriate for nearest-neighbour distance calculations. It does not
    perform buffer-based spatial joins. For buffer-based aggregation, use
    :func:`features_proximity_agg`.

    Examples
    --------
    Calculate the nearest vendor distance for each household:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> households = pd.DataFrame(
    ...     {
    ...         "household_id": [1, 2],
    ...         "_longitude": [36.8001, 36.9000],
    ...         "_latitude": [-1.3001, -1.4000],
    ...     }
    ... )
    >>> vendors = pd.DataFrame(
    ...     {
    ...         "vendor_id": [1, 2],
    ...         "vendor_type": ["shop", "kiosk"],
    ...         "_longitude": [36.8000, 36.8500],
    ...         "_latitude": [-1.3000, -1.3500],
    ...     }
    ... )
    >>> result = nfei.calc_distance(
    ...     data1=households,
    ...     data2=vendors,
    ...     include_col="vendor_type",
    ... )

    Use custom coordinate column names:

    >>> result = nfei.calc_distance(
    ...     data1=households.rename(
    ...         columns={"_longitude": "lon", "_latitude": "lat"}
    ...     ),
    ...     data2=vendors.rename(
    ...         columns={"_longitude": "x", "_latitude": "y"}
    ...     ),
    ...     data1_lon="lon",
    ...     data1_lat="lat",
    ...     data2_lon="x",
    ...     data2_lat="y",
    ...     col_title="nearest_vendor_km",
    ... )
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
    Aggregate features within a spatial buffer.

    This function aggregates features from ``df2`` within a specified buffer
    around each observation in ``df1``. It supports NFEI workflows where users
    need to construct environment-level indicators, such as food diversity
    within 50 metres of each vendor or access to sanitation facilities within a
    specified distance.

    The function accepts ordinary pandas DataFrames with longitude and latitude
    columns. Internally, it converts the data to projected GeoDataFrames, creates
    buffers around ``df1`` points, performs a spatial join, and aggregates
    matching ``df2`` observations within each buffer.

    Parameters
    ----------
    df1:
        Primary dataframe. A buffer is created around each row in this
        dataframe, and aggregated values are returned at this level.

    df2:
        Secondary dataframe containing the features to aggregate within each
        buffer.

    buffer:
        Buffer radius in metres.

    col_to_agg:
        List of columns in ``df2`` to aggregate. Required when ``method`` is
        ``"sum"``, ``"mean"``, or ``"max"``. Not required when
        ``method="count"``.

    self_count:
        If False and ``df1`` and ``df2`` are the same object, each row is
        excluded from its own buffer before aggregation. If True, each row can
        contribute to its own buffer.

    include_sum:
        If True and ``method`` is not ``"count"``, adds an overall aggregate
        column by summing the aggregated columns row-wise.

    method:
        Aggregation method. Must be one of ``"sum"``, ``"mean"``, ``"max"``,
        or ``"count"``.

    df1_lat:
        Latitude column name in ``df1``. The default is ``"_latitude"``.

    df1_lon:
        Longitude column name in ``df1``. The default is ``"_longitude"``.

    df2_lat:
        Latitude column name in ``df2``. The default is ``"_latitude"``.

    df2_lon:
        Longitude column name in ``df2``. The default is ``"_longitude"``.

    overall_title:
        Name of the output count column when ``method="count"``, or the overall
        aggregate column when ``include_sum=True``.

    drop_col_to_agg:
        If True, drops the individual aggregated columns and keeps only
        ``overall_title``. This is only valid when ``include_sum=True`` and
        ``method`` is not ``"count"``.

    input_crs:
        Coordinate reference system of the input longitude and latitude
        coordinates. The default is ``"EPSG:4326"``.

    projected_crs:
        Projected coordinate reference system used for buffer and distance
        operations. If None, a local UTM CRS is estimated from the input
        coordinates.

    Returns
    -------
    pd.DataFrame
        Copy of ``df1`` with buffer-based aggregate columns added.

    Raises
    ------
    ValueError
        If ``buffer`` is less than or equal to zero, if ``method`` is invalid,
        if ``col_to_agg`` is missing when required, or if
        ``drop_col_to_agg=True`` is used without ``include_sum=True`` for
        non-count aggregation.

    KeyError
        If coordinate columns are missing, or if any column listed in
        ``col_to_agg`` is not found in ``df2``.

    Notes
    -----
    The ``buffer`` argument is in metres because the function performs buffer
    operations in a projected CRS.

    When ``df1`` and ``df2`` are the same object, ``self_count=False`` excludes
    each observation from its own buffer. This is useful for neighbour-only
    calculations. Use ``self_count=True`` when the focal observation should be
    included in its own environment, such as when computing food diversity
    available within a vendor's immediate environment including the vendor
    itself.

    Output column names for non-count aggregation are generated by appending
    ``"_within_{buffer}m"`` to aggregated column names.

    Rows with no matching features within the buffer receive 0 in the added
    aggregate columns.

    Examples
    --------
    Count vendors within 100 metres of each household:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> households = pd.DataFrame(
    ...     {
    ...         "household_id": [1, 2],
    ...         "_longitude": [36.8001, 36.9000],
    ...         "_latitude": [-1.3001, -1.4000],
    ...     }
    ... )
    >>> vendors = pd.DataFrame(
    ...     {
    ...         "vendor_id": [1, 2],
    ...         "_longitude": [36.8000, 36.8500],
    ...         "_latitude": [-1.3000, -1.3500],
    ...     }
    ... )
    >>> result = nfei.features_proximity_agg(
    ...     df1=households,
    ...     df2=vendors,
    ...     buffer=100,
    ...     method="count",
    ...     overall_title="vendors_within_100m",
    ... )

    Sum food-group availability within 50 metres of each vendor:

    >>> vendors = pd.DataFrame(
    ...     {
    ...         "vendor_id": [1, 2],
    ...         "_longitude": [36.8000, 36.8002],
    ...         "_latitude": [-1.3000, -1.3002],
    ...         "grains": [1, 1],
    ...         "legumes_pulses": [1, 0],
    ...         "other_vegetables": [0, 1],
    ...     }
    ... )
    >>> result = nfei.features_proximity_agg(
    ...     df1=vendors,
    ...     df2=vendors,
    ...     buffer=50,
    ...     col_to_agg=["grains", "legumes_pulses", "other_vegetables"],
    ...     method="sum",
    ...     self_count=True,
    ... )

    Create a single overall aggregate column and drop individual columns:

    >>> result = nfei.features_proximity_agg(
    ...     df1=vendors,
    ...     df2=vendors,
    ...     buffer=50,
    ...     col_to_agg=["grains", "legumes_pulses", "other_vegetables"],
    ...     method="sum",
    ...     self_count=True,
    ...     include_sum=True,
    ...     overall_title="food_group_items_within_50m",
    ...     drop_col_to_agg=True,
    ... )
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