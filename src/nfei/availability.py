from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_TIME_WEIGHTS = {
    "morning": 30,
    "afternoon": 30,
    "evening": 30,
    "night": 10,
}

VALID_MISSING_POLICIES = {"raise", "fill", "ignore"}


def _validate_missing_policy(missing_policy: str) -> None:
    if missing_policy not in VALID_MISSING_POLICIES:
        raise ValueError(
            "missing_policy must be one of: 'raise', 'fill', or 'ignore'."
        )


def _validate_required_columns(df: pd.DataFrame, required_cols: list[str]) -> None:
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required column(s): {missing_cols}")


def add_daily_availability(
    df: pd.DataFrame,
    time_cols: dict[str, str],
    all_day_col: str | None = None,
    time_weights: dict[str, float] | None = None,
    output_col: str = "perc_daily_avail",
    fillna_value: int | float = 0,
    missing_policy: str = "raise",
) -> pd.DataFrame:
    """
    Add percentage daily vendor availability.

    Daily availability is calculated from user-specified binary time-period
    columns. By default, the function follows the NFEI notebook weighting:
    morning=30, afternoon=30, evening=30, night=10.

    If all_day_col is provided and equals 1, daily availability is set to 100,
    even if the time-period columns are missing. This supports questionnaires
    where time-period questions are skipped when the respondent indicates
    all-day availability.

    Parameters
    ----------
    df:
        Input dataframe.

    time_cols:
        Dictionary mapping time-period labels to dataframe column names.

    all_day_col:
        Optional binary column indicating whether the vendor operates all day.

    time_weights:
        Dictionary mapping the same time-period labels to percentage weights.

    output_col:
        Name of the output daily availability column.

    fillna_value:
        Value used to fill missing values when missing_policy='fill'.

    missing_policy:
        How to handle missing values in time_cols.

        - 'raise': raise an error for missing time values unless all_day_col == 1.
        - 'fill': fill missing time values with fillna_value.
        - 'ignore': leave missing values as-is.

    Returns
    -------
    pd.DataFrame
        Copy of dataframe with percentage daily availability added.
    """
    _validate_missing_policy(missing_policy)

    if time_weights is None:
        time_weights = DEFAULT_TIME_WEIGHTS.copy()

    if set(time_cols.keys()) != set(time_weights.keys()):
        raise ValueError("time_cols and time_weights must contain the same keys.")

    time_col_names = list(time_cols.values())
    required_cols = time_col_names.copy()

    if all_day_col is not None:
        required_cols.append(all_day_col)

    _validate_required_columns(df, required_cols)

    new_df = df.copy()

    if missing_policy == "raise":
        if all_day_col is not None:
            rows_to_check = new_df[all_day_col] != 1
            missing_mask = new_df.loc[rows_to_check, time_col_names].isna().any(axis=1)

            if missing_mask.any():
                raise ValueError(
                    "Missing values found in time_cols for rows where "
                    "all_day_col is not 1. Clean these values, set "
                    "missing_policy='fill', or confirm that all_day_col "
                    "correctly identifies all-day availability."
                )
        else:
            missing_mask = new_df[time_col_names].isna().any(axis=1)

            if missing_mask.any():
                raise ValueError(
                    "Missing values found in time_cols, but all_day_col was "
                    "not provided. Provide all_day_col if missing time-period "
                    "values are structurally valid, or set missing_policy='fill' "
                    "if missing values should be treated as 0."
                )

    elif missing_policy == "fill":
        new_df[time_col_names] = new_df[time_col_names].fillna(fillna_value)

        if all_day_col is not None:
            new_df[all_day_col] = new_df[all_day_col].fillna(fillna_value)

    weighted_score = sum(
        new_df[col_name] * time_weights[time_label]
        for time_label, col_name in time_cols.items()
    )

    if all_day_col is not None:
        new_df[output_col] = np.where(
            new_df[all_day_col] == 1,
            100,
            weighted_score,
        )
    else:
        new_df[output_col] = weighted_score

    return new_df


def add_weekly_availability(
    df: pd.DataFrame,
    day_cols: list[str],
    all_week_col: str | None = None,
    output_col: str = "perc_weekly_avail",
    days_in_week: int = 7,
    fillna_value: int | float = 0,
    round_result: bool = False,
    missing_policy: str = "raise",
) -> pd.DataFrame:
    """
    Add percentage weekly vendor availability.

    Weekly availability is calculated as the percentage of available days in a
    week. If all_week_col is provided and equals 1, weekly availability is set
    to 100, even if individual day columns are missing.

    Parameters
    ----------
    df:
        Input dataframe.

    day_cols:
        List of binary day columns. By default, this should contain 7 columns.

    all_week_col:
        Optional binary column indicating whether the vendor operates all week.

    output_col:
        Name of the output weekly availability column.

    days_in_week:
        Number of days used as the denominator. Default is 7.

    fillna_value:
        Value used to fill missing values when missing_policy='fill'.

    round_result:
        If True, converts the result to integer percentage.

    missing_policy:
        How to handle missing values in day_cols.

        - 'raise': raise an error for missing day values unless all_week_col == 1.
        - 'fill': fill missing day values with fillna_value.
        - 'ignore': leave missing values as-is.

    Returns
    -------
    pd.DataFrame
        Copy of dataframe with percentage weekly availability added.
    """
    _validate_missing_policy(missing_policy)

    if days_in_week <= 0:
        raise ValueError("days_in_week must be greater than zero.")

    if len(day_cols) != days_in_week:
        raise ValueError(
            "The number of day_cols must match days_in_week. "
            f"Got {len(day_cols)} day_cols and days_in_week={days_in_week}."
        )

    required_cols = list(day_cols)

    if all_week_col is not None:
        required_cols.append(all_week_col)

    _validate_required_columns(df, required_cols)

    new_df = df.copy()

    if missing_policy == "raise":
        if all_week_col is not None:
            rows_to_check = new_df[all_week_col] != 1
            missing_mask = new_df.loc[rows_to_check, day_cols].isna().any(axis=1)

            if missing_mask.any():
                raise ValueError(
                    "Missing values found in day_cols for rows where "
                    "all_week_col is not 1. Clean these values, set "
                    "missing_policy='fill', or confirm that all_week_col "
                    "correctly identifies all-week availability."
                )
        else:
            missing_mask = new_df[day_cols].isna().any(axis=1)

            if missing_mask.any():
                raise ValueError(
                    "Missing values found in day_cols, but all_week_col was "
                    "not provided. Provide all_week_col if missing day values "
                    "are structurally valid, or set missing_policy='fill' if "
                    "missing values should be treated as 0."
                )

    elif missing_policy == "fill":
        new_df[day_cols] = new_df[day_cols].fillna(fillna_value)

        if all_week_col is not None:
            new_df[all_week_col] = new_df[all_week_col].fillna(fillna_value)

    weekly_score = new_df[day_cols].sum(axis=1) / days_in_week * 100

    if all_week_col is not None:
        new_df[output_col] = np.where(
            new_df[all_week_col] == 1,
            100,
            weekly_score,
        )
    else:
        new_df[output_col] = weekly_score

    if round_result:
        new_df[output_col] = new_df[output_col].astype(int)

    return new_df


def add_vendor_availability(
    df: pd.DataFrame,
    daily_col: str = "perc_daily_avail",
    weekly_col: str = "perc_weekly_avail",
    output_col: str = "perc_vendor_avail",
) -> pd.DataFrame:
    """
    Add overall vendor availability as the mean of daily and weekly availability.
    """
    required_cols = [daily_col, weekly_col]
    _validate_required_columns(df, required_cols)

    new_df = df.copy()
    new_df[output_col] = new_df[[daily_col, weekly_col]].mean(axis=1)

    return new_df