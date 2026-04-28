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

    This function identifies outliers in numeric data using the Median Absolute
    Deviation (MAD) approach. It is used in the NFEI workflow to detect extreme
    values in skewed distributions, particularly for spatial coordinates where
    traditional mean-based methods are not robust.

    The MAD method is preferred because it is resistant to the influence of
    extreme values and works well for non-normal data.

    Parameters
    ----------
    values:
        One-dimensional numeric values, provided as a pandas Series or NumPy array.

    threshold:
        Modified Z-score threshold used to flag outliers. Observations with a
        modified Z-score greater than this threshold are classified as outliers.
        The default is 3.0.

    Returns
    -------
    pd.Series
        Boolean Series where True indicates an outlier.

    Raises
    ------
    ValueError
        If ``values`` is empty.

    TypeError
        If ``values`` is not numeric.

    Notes
    -----
    The modified Z-score is calculated as:

    ``0.6745 * |x - median| / MAD``

    where MAD is the median absolute deviation.

    If MAD is equal to zero, the function returns False for all observations,
    as no variation exists to detect outliers.

    This function is commonly used as a building block for spatial data cleaning,
    particularly in :func:`fix_spatial_outliers`.

    Examples
    --------
    Detect outliers in a numeric series:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> values = pd.Series([1, 2, 2, 3, 100])
    >>> outliers = nfei.mad_based_outlier(values)
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
    Detect and correct spatial coordinate outliers.

    This function identifies and corrects outliers in geographic coordinate data
    using the Median Absolute Deviation (MAD) method. It is designed for NFEI
    workflows where inaccurate latitude and longitude values can distort
    distance calculations, spatial aggregation, and density estimation.

    The function detects outliers separately in latitude and longitude, then
    combines both flags. A row is treated as a spatial outlier if either its
    latitude or longitude is flagged as an outlier.

    Outlying coordinates are replaced using the median latitude and longitude
    calculated from non-outlier observations.

    Parameters
    ----------
    df:
        Input dataframe containing coordinate columns.

    latitude:
        Name of the latitude column.

    longitude:
        Name of the longitude column.

    threshold:
        Modified Z-score threshold used for MAD-based outlier detection.
        The default is 3.0.

    return_outlier_flag:
        If True, adds a boolean column indicating which rows were flagged as
        spatial outliers.

    outlier_col:
        Name of the outlier flag column when ``return_outlier_flag=True``.

    show_plots:
        If True, displays before and after scatter plots showing detected and
        corrected outliers.

    Returns
    -------
    pd.DataFrame
        Copy of the dataframe with corrected coordinates. If
        ``return_outlier_flag=True``, an additional boolean column is included.

    Raises
    ------
    KeyError
        If ``latitude`` or ``longitude`` columns are not found in the dataframe.

    TypeError
        If coordinate columns are not numeric.

    ValueError
        If all rows are flagged as outliers, making it impossible to compute
        replacement values.

    Notes
    -----
    This function applies MAD-based outlier detection independently to
    latitude and longitude, then combines both flags.

    Replacement values are computed as:

    - median latitude of non-outliers
    - median longitude of non-outliers

    This ensures that corrected coordinates remain within the central spatial
    distribution of the dataset.

    Plotting is optional and controlled by ``show_plots``. In production
    workflows, it is recommended to set ``show_plots=False`` to avoid rendering
    overhead.

    Examples
    --------
    Correct spatial outliers in coordinate data:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "lat": [-1.30, -1.31, -50.0],
    ...         "lon": [36.80, 36.81, 100.0],
    ...     }
    ... )
    >>> result = nfei.fix_spatial_outliers(
    ...     df,
    ...     latitude="lat",
    ...     longitude="lon",
    ...     show_plots=False,
    ... )

    Return an outlier flag column:

    >>> result = nfei.fix_spatial_outliers(
    ...     df,
    ...     latitude="lat",
    ...     longitude="lon",
    ...     return_outlier_flag=True,
    ...     show_plots=False,
    ... )
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