from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def mad_based_outlier(
    values: pd.Series | np.ndarray,
    threshold: float = 3.0,
) -> pd.Series:
    """
    Detect outliers using the Median Absolute Deviation (MAD) method.

    This function mirrors the outlier detection logic used in the original NFEI
    notebooks. It is useful for identifying unusually distant coordinate values
    or extreme numeric observations in skewed data.

    Parameters
    ----------
    values:
        One-dimensional numeric values, either as a pandas Series or NumPy array.

    threshold:
        Modified Z-score threshold used to flag outliers. Values with modified
        Z-scores greater than this threshold are flagged as outliers. The default
        is 3.0, matching the original notebook function.

    Returns
    -------
    pd.Series
        Boolean Series where True indicates an outlier.

    Notes
    -----
    The modified Z-score is calculated as:

        0.6745 * abs(x - median) / MAD

    If MAD is zero, the function returns False for all observations because
    there is no usable variation for detecting outliers.
    """
    series = pd.Series(values)

    if series.empty:
        raise ValueError("values must contain at least one observation.")

    if not pd.api.types.is_numeric_dtype(series):
        raise TypeError("values must be numeric.")

    median = np.median(series)
    deviation = np.abs(series - median)
    mad = np.median(deviation)

    if mad == 0:
        return pd.Series([False] * len(series), index=series.index)

    modified_z_score = 0.6745 * deviation / mad

    return modified_z_score > threshold


def fix_spatial_outliers(
    df: pd.DataFrame,
    latitude: str,
    longitude: str,
    threshold: float = 3.0,
    return_outlier_flag: bool = False,
    outlier_col: str = "spatial_outlier",
    show_plots: bool = True,
) -> pd.DataFrame:
    """
    Detect and correct spatial coordinate outliers using longitude and latitude.

    This function applies MAD-based outlier detection separately to longitude and latitude,
    combines both outlier flags, and replaces outlying coordinates with the
    median longitude and latitude of the non-outlying observations.

    Parameters
    ----------
    df:
        Input dataframe containing coordinate columns.

    latitude:
        Name of the latitude column.

    longitude:
        Name of the longitude column.

    threshold:
        Modified Z-score threshold for MAD-based outlier detection. The default
        is 3.0, matching the original notebook.

    return_outlier_flag:
        If True, adds a boolean column identifying rows that were flagged as
        spatial outliers.

    outlier_col:
        Name of the outlier flag column added when return_outlier_flag=True.

    show_plots:
        If True, displays before and after scatter plots.

    Returns
    -------
    pd.DataFrame
        Dataframe with spatial outliers corrected. If return_outlier_flag=True,
        an additional boolean column is included.

    Notes
    -----
    A row is treated as a spatial outlier if either its longitude or latitude is
    flagged as an outlier. Both longitude and latitude are then replaced using
    the median coordinates calculated only from non-outlier rows.

    The original notebook plotted before and after maps. Plotting is not included
    here because package functions should avoid side effects. We can add a
    separate plotting helper later if needed.
    """
    missing_cols = [col for col in [latitude, longitude] if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing coordinate column(s): {missing_cols}")

    if not pd.api.types.is_numeric_dtype(df[latitude]):
        raise TypeError(f"Latitude column '{latitude}' must be numeric.")

    if not pd.api.types.is_numeric_dtype(df[longitude]):
        raise TypeError(f"Longitude column '{longitude}' must be numeric.")

    # Create a copy to avoid modifying the original dataframe
    new_df = df.copy()

    # Detect outliers separately for longitude and latitude
    outliers_longitude = mad_based_outlier(new_df[longitude], threshold=threshold)
    outliers_latitude = mad_based_outlier(new_df[latitude], threshold=threshold)

    # Combine outlier flags: a row is an outlier if either longitude or latitude is an outlier
    outliers = outliers_longitude | outliers_latitude

    if outliers.all():
        raise ValueError(
            "All rows flagged as outliers. Cannot compute replacement values."
        )

    # Optionally show the before plot with outliers highlighted
    if show_plots:
        plt.figure(figsize=(10, 6))
        plt.scatter(
            new_df.loc[~outliers, longitude],
            new_df.loc[~outliers, latitude],
            c="blue",
            label="Inliers",
        )
        plt.scatter(
            new_df.loc[outliers, longitude],
            new_df.loc[outliers, latitude],
            c="red",
            label="Outliers",
        )
        plt.xlabel(longitude)
        plt.ylabel(latitude)
        plt.title("MAD Outlier Detection (Before Correction)")
        plt.legend()
        plt.show()

    # Replace using inlier medians
    median_lon = new_df.loc[~outliers, longitude].median()
    median_lat = new_df.loc[~outliers, latitude].median()

    new_df.loc[outliers, longitude] = median_lon
    new_df.loc[outliers, latitude] = median_lat

    # Optionally show the after plot with corrected points
    if show_plots:
        plt.figure(figsize=(10, 6))
        plt.scatter(
            new_df[longitude],
            new_df[latitude],
            c="blue",
            label="Corrected Points",
        )
        plt.xlabel(longitude)
        plt.ylabel(latitude)
        plt.title("MAD Outlier Detection (After Correction)")
        plt.legend()
        plt.show()

    if return_outlier_flag:
        new_df[outlier_col] = outliers.to_numpy()

    return new_df