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
    This function computes the daily component of vendor availability used in
    the NFEI workflow. It converts binary time-period availability columns into
    a percentage score that reflects the share of the day during which a vendor
    is accessible to consumers.
    
    By default, the function follows the NFEI notebook weighting scheme:

    - ``morning``: 30
    - ``afternoon``: 30
    - ``evening``: 30
    - ``night``: 10

    These weights reflect the assumption that most food purchasing activity
    occurs from morning to evening, while night-time availability contributes a
    smaller share to overall daily access.

    Parameters
    ----------
    df:
        Input dataframe.

    time_cols:
        Dictionary mapping the required time-period labels to dataframe column
        names. The required keys are ``"morning"``, ``"afternoon"``,
        ``"evening"``, and ``"night"``.

    all_day_col:
        Optional binary column indicating whether the vendor operates all day.
        If provided and equal to 1, the daily availability score is set to 100.

    time_weights:
        Optional dictionary mapping the same time-period labels in
        ``time_cols`` to percentage weights. If None, the default NFEI weights
        are used. Custom weights must use the same keys as ``time_cols``.
        Users should ensure the weights sum to 100 for direct percentage
        interpretation.

    output_col:
        Name of the output daily availability column.

    fillna_value:
        Value used to fill missing values when ``missing_policy="fill"``.

    missing_policy:
        How to handle missing values in ``time_cols``.

        - ``"raise"``: raise an error for missing time values unless
          ``all_day_col == 1``.
        - ``"fill"``: fill missing time values with ``fillna_value``.
        - ``"ignore"``: leave missing values as-is.

    Returns
    -------
    pd.DataFrame
        Copy of the dataframe with the daily availability percentage column
        added.

    Raises
    ------
    KeyError
        If any required time-period column, or the optional ``all_day_col``,
        is not found in the dataframe.

    ValueError
        If ``time_cols`` and ``time_weights`` do not contain the same keys, if
        ``missing_policy`` is invalid, or if missing values are found under
        ``missing_policy="raise"``.

    Notes
    -----
    Missing values are handled conservatively by default. When
    ``missing_policy="raise"``, missing values in ``time_cols`` are allowed only
    for rows where ``all_day_col == 1``. This supports survey designs where
    time-period questions are skipped after an all-day response.

    If ``all_day_col`` is not provided, missing values in ``time_cols`` are
    treated as a data-quality issue unless ``missing_policy="fill"`` or
    ``missing_policy="ignore"`` is used.

    Examples
    --------
    Standard use with an all-day column:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "vendor_allday": [0, 1],
    ...         "available_morning": [1, None],
    ...         "available_afternoon": [1, None],
    ...         "available_evening": [0, None],
    ...         "available_night": [0, None],
    ...     }
    ... )
    >>> time_cols = {
    ...     "morning": "available_morning",
    ...     "afternoon": "available_afternoon",
    ...     "evening": "available_evening",
    ...     "night": "available_night",
    ... }
    >>> result = nfei.add_daily_availability(
    ...     df,
    ...     time_cols=time_cols,
    ...     all_day_col="vendor_allday",
    ... )

    Custom weighting:

    >>> result = nfei.add_daily_availability(
    ...     df,
    ...     time_cols=time_cols,
    ...     all_day_col="vendor_allday",
    ...     time_weights={
    ...         "morning": 25,
    ...         "afternoon": 25,
    ...         "evening": 25,
    ...         "night": 25,
    ...     },
    ... )
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
    This function computes the weekly component of vendor availability used in
    the NFEI workflow. It converts binary day-of-week availability columns into
    a percentage score that reflects how consistently a vendor is accessible
    across the week.

    By default, the function expects seven binary day columns, one for each day
    of the week, and calculates availability as:

    ``number of available days / days_in_week * 100``

    If ``all_week_col`` is provided and equals 1, weekly availability is set to
    100, even if the individual day columns are missing. This supports survey
    designs where individual day questions are skipped after an all-week
    response.

    Parameters
    ----------
    df:
        Input dataframe.

    day_cols:
        List of binary day-of-week columns. By default, this should contain
        seven columns, one for each day of the week.

    all_week_col:
        Optional binary column indicating whether the vendor operates all week.
        If provided and equal to 1, the weekly availability score is set to 100.

    output_col:
        Name of the output weekly availability column.

    days_in_week:
        Number of days used as the denominator. The default is 7.

    fillna_value:
        Value used to fill missing values when ``missing_policy="fill"``.

    round_result:
        If True, converts the weekly availability score to an integer
        percentage. This is useful when matching notebook workflows where
        percentage availability was stored as rounded whole numbers.

    missing_policy:
        How to handle missing values in ``day_cols``.

        - ``"raise"``: raise an error for missing day values unless
          ``all_week_col == 1``.
        - ``"fill"``: fill missing day values with ``fillna_value``.
        - ``"ignore"``: leave missing values as-is.

    Returns
    -------
    pd.DataFrame
        Copy of the dataframe with the weekly availability percentage column
        added.

    Raises
    ------
    KeyError
        If any required day column, or the optional ``all_week_col``, is not
        found in the dataframe.

    ValueError
        If ``days_in_week`` is less than or equal to zero, if the number of
        ``day_cols`` does not match ``days_in_week``, if ``missing_policy`` is
        invalid, or if missing values are found under
        ``missing_policy="raise"``.

    Notes
    -----
    The default configuration assumes a standard seven-day week. If a different
    denominator is used, ``day_cols`` must contain the same number of columns as
    ``days_in_week``.

    Missing values are handled conservatively by default. When
    ``missing_policy="raise"``, missing values in ``day_cols`` are allowed only
    for rows where ``all_week_col == 1``.

    If ``all_week_col`` is not provided, missing values in ``day_cols`` are
    treated as a data-quality issue unless ``missing_policy="fill"`` or
    ``missing_policy="ignore"`` is used.

    Examples
    --------
    Standard use with an all-week column:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "vendor_allweek": [0, 1],
    ...         "monday": [1, None],
    ...         "tuesday": [1, None],
    ...         "wednesday": [1, None],
    ...         "thursday": [0, None],
    ...         "friday": [0, None],
    ...         "saturday": [0, None],
    ...         "sunday": [0, None],
    ...     }
    ... )
    >>> day_cols = [
    ...     "monday",
    ...     "tuesday",
    ...     "wednesday",
    ...     "thursday",
    ...     "friday",
    ...     "saturday",
    ...     "sunday",
    ... ]
    >>> result = nfei.add_weekly_availability(
    ...     df,
    ...     day_cols=day_cols,
    ...     all_week_col="vendor_allweek",
    ... )

    Use without an all-week column when all day columns are collected directly:

    >>> df = pd.DataFrame(
    ...     {
    ...         "monday": [1],
    ...         "tuesday": [1],
    ...         "wednesday": [1],
    ...         "thursday": [0],
    ...         "friday": [0],
    ...         "saturday": [0],
    ...         "sunday": [0],
    ...     }
    ... )
    >>> result = nfei.add_weekly_availability(
    ...     df,
    ...     day_cols=day_cols,
    ...     all_week_col=None,
    ...     round_result=True,
    ... )
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
    This function computes the combined vendor availability indicator used in
    the NFEI workflow. It summarizes temporal access to vendors by taking the
    row-wise mean of daily availability and weekly availability.

    The function assumes that daily and weekly availability have already been
    computed, typically using :func:`add_daily_availability` and
    :func:`add_weekly_availability`. The resulting score provides a single
    percentage-based measure of how consistently a vendor is available both
    within a day and across the week.

    Parameters
    ----------
    df:
        Input dataframe.

    daily_col:
        Column containing percentage daily availability. The default is
        ``"perc_daily_avail"``.

    weekly_col:
        Column containing percentage weekly availability. The default is
        ``"perc_weekly_avail"``.

    output_col:
        Name of the output column containing overall vendor availability. The
        default is ``"perc_vendor_avail"``.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the combined vendor availability
        column added.

    Raises
    ------
    KeyError
        If either ``daily_col`` or ``weekly_col`` is not found in the dataframe.

    Notes
    -----
    The output is calculated as:

    ``(daily availability + weekly availability) / 2``

    The function does not rescale the inputs. Users should ensure that both
    input columns are measured on the same percentage scale, usually 0 to 100.

    Examples
    --------
    Standard use with default column names:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "perc_daily_avail": [100, 60],
    ...         "perc_weekly_avail": [100, 40],
    ...     }
    ... )
    >>> result = nfei.add_vendor_availability(df)

    Use with custom column names:

    >>> result = nfei.add_vendor_availability(
    ...     df,
    ...     daily_col="perc_daily_avail",
    ...     weekly_col="perc_weekly_avail",
    ...     output_col="vendor_availability_score",
    ... )
    """
    
    required_cols = [daily_col, weekly_col]
    _validate_required_columns(df, required_cols)

    new_df = df.copy()
    new_df[output_col] = new_df[[daily_col, weekly_col]].mean(axis=1)

    return new_df