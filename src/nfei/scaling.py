from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def create_linear_scale(
    df: pd.DataFrame,
    col: str,
    expected_max: float | None = None,
    min_scale: float = 0,
    max_scale: float = 10,
    invert: bool = False,
    var_title: str | None = None,
    drop_intermediate: bool = True,
) -> pd.DataFrame:
    """
    Create a linearly scaled indicator.

    This function transforms a numeric column into a standardized score using
    linear scaling. It is used in the NFEI workflow to align indicators with
    different units and ranges onto a common interpretation scale, typically
    from 0 to 10.

    The function first normalizes the selected column to a 0–1 range using
    Min-Max scaling. It can optionally adjust this normalization using an
    expected maximum value, invert the resulting scores, and then rescale them
    to a user-defined range.

    Parameters
    ----------
    df:
        Input dataframe.

    col:
        Name of the numeric column to be scaled.

    expected_max:
        Optional theoretical or expected maximum value for the indicator. If
        provided, the normalized values are adjusted so that scores remain
        interpretable relative to this expected maximum, rather than only the
        observed maximum in the data.

    min_scale:
        Lower bound of the final scale. The default is 0.

    max_scale:
        Upper bound of the final scale. The default is 10.

    invert:
        If True, higher original values receive lower scaled scores. This is
        typically used for indicators where higher values represent less
        desirable conditions, such as unhealthy food exposure.

    var_title:
        Name of the output scaled column. If None, a default name is generated
        as ``"{col}_scaled"``.

    drop_intermediate:
        If True, intermediate normalization columns are removed from the
        dataframe. If False, intermediate columns are retained for inspection.
        Intermediate columns are named using the input column name:
        ``"_{col}_normalized"`` and ``"_{col}_final_normalized"``.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the scaled indicator column added.

    Raises
    ------
    KeyError
        If ``col`` is not found in the dataframe.

    ValueError
        If ``max_scale`` is less than or equal to ``min_scale``.

    Notes
    -----
    The scaling process follows three steps:

    1. Normalize the input column to a 0–1 range using Min-Max scaling.
    2. Optionally adjust normalized values using ``expected_max``.
    3. Rescale the values to the specified range:

       ``min_scale + normalized * (max_scale - min_scale)``

    If ``invert=True``, the normalized values are transformed as:

    ``1 - normalized``

    before rescaling.

    The ``expected_max`` parameter is particularly important when working with
    indicators that have a known theoretical upper bound. It prevents artificially
    high scores when the observed maximum in the dataset is lower than what is
    theoretically possible.

    Examples
    --------
    Scale an indicator to the default 0–10 range:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "unhealthy_food_count": [0, 5, 10]
    ...     }
    ... )
    >>> result = nfei.create_linear_scale(
    ...     df,
    ...     col="unhealthy_food_count",
    ... )

    Invert the scale so higher values represent better conditions:

    >>> result = nfei.create_linear_scale(
    ...     df,
    ...     col="unhealthy_food_count",
    ...     invert=True,
    ... )

    Use an expected maximum to stabilize interpretation:

    >>> result = nfei.create_linear_scale(
    ...     df,
    ...     col="unhealthy_food_count",
    ...     expected_max=15,
    ... )

    Retain intermediate columns for debugging:

    >>> result = nfei.create_linear_scale(
    ...     df,
    ...     col="unhealthy_food_count",
    ...     drop_intermediate=False,
    ... )
    """
    
    # Validate inputs
    if col not in df.columns:
        raise KeyError(f"Column '{col}' was not found in the dataframe.")

    if max_scale <= min_scale:
        raise ValueError("max_scale must be greater than min_scale.")

    if var_title is None:
        var_title = f"{col}_scaled"

    normalized_col = f"_{col}_normalized"
    final_normalized_col = f"_{col}_final_normalized"

    # Create a copy of the dataframe to avoid modifying the original
    new_df = df.copy()

    # Normalize the column to [0, 1]
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized = scaler.fit_transform(new_df[[col]]).ravel()

    # If an expected maximum is provided, adjust the normalized values so scores
    # remain interpretable relative to the expected maximum.
    if expected_max is not None:
        actual_max = new_df[col].max()
        scaling_factor = min(actual_max, expected_max)
        normalized = normalized * (scaling_factor / expected_max)

    new_df[normalized_col] = normalized

    # Invert the normalized values if requested
    if invert:
        new_df[final_normalized_col] = 1 - new_df[normalized_col]
    else:
        new_df[final_normalized_col] = new_df[normalized_col]

    # Scale the final normalized values to the specified range
    new_df[var_title] = (
        min_scale + new_df[final_normalized_col] * (max_scale - min_scale)
    ).round(2)

    # Drop intermediate columns if requested
    if drop_intermediate:
        new_df = new_df.drop(columns=[normalized_col, final_normalized_col])

    return new_df