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
    Create a linearly scaled indicator from a numeric column.

    This function mirrors the original NFEI notebook logic. It normalizes a
    selected column, optionally adjusts scaling using an expected maximum,
    optionally inverts the score, and adds a new scaled indicator column.

    Parameters
    ----------
    df:
        Input dataframe.
    col:
        Column to scale.
    expected_max:
        The theoretical or expected maximum value. If provided, the observed
        maximum is compared with this value so that scores remain interpretable
        relative to the expected maximum.
    min_scale:
        Lower bound of the final scale.
    max_scale:
        Upper bound of the final scale.
    invert:
        If True, higher original values receive lower scaled scores.
    var_title:
        Name of the new scaled column. If None, a default name is generated.
    drop_intermediate:
        If True, intermediate normalization columns are removed.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the new scaled indicator column added.
    """
    # Validate inputs
    if col not in df.columns:
        raise KeyError(f"Column '{col}' was not found in the dataframe.")

    if max_scale <= min_scale:
        raise ValueError("max_scale must be greater than min_scale.")

    if var_title is None:
        var_title = f"{col}_scaled"

    # Create a copy of the dataframe to avoid modifying the original
    new_df = df.copy()

    # Normalize the column to [0, 1]
    scaler = MinMaxScaler(feature_range=(0, 1))
    normalized = scaler.fit_transform(new_df[[col]]).ravel()

    # If an expected maximum is provided, adjust the normalized values to ensure they are interpretable relative to this expected maximum
    if expected_max is not None:
        actual_max = new_df[col].max()
        scaling_factor = min(actual_max, expected_max)
        normalized = normalized * (scaling_factor / expected_max)

    new_df["Normalized_col"] = normalized

    # Invert the normalized values if requested
    if invert:
        new_df["Final_Normalized"] = 1 - new_df["Normalized_col"]
    else:
        new_df["Final_Normalized"] = new_df["Normalized_col"]

    # Scale the final normalized values to the specified range and round to 2 decimal places
    new_df[var_title] = (
        min_scale + new_df["Final_Normalized"] * (max_scale - min_scale)
    ).round(2)

    # Drop intermediate columns if requested
    if drop_intermediate:
        new_df = new_df.drop(columns=["Normalized_col", "Final_Normalized"])

    return new_df