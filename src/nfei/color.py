from __future__ import annotations

import pandas as pd


DEFAULT_COLOR_GROUPS = [
    "White_Brown",
    "Yellow_Orange",
    "Green_other",
    "Dark_leafy_green",
    "Red",
    "Purple_Blue",
]


def count_unique_colors_in_columns(
    df: pd.DataFrame,
    columns: list[str],
    output_col: str = "unique_color_count",
) -> pd.Series:
    """
    This helper function counts the number of distinct produce color groups
    recorded for each observation across one or more dataframe columns. It is
    useful when produce color information is spread across multiple columns,
    such as separate fruit and vegetable color fields.

    The function supports comma-separated color values within each cell, which
    reflects the format used in the original NFEI notebook workflows.

    Parameters
    ----------
    df:
        Input dataframe.

    columns:
        List of columns containing produce color values. Values may be single
        color names or comma-separated color names.

    output_col:
        Name assigned to the returned pandas Series. The default is
        ``"unique_color_count"``.

    Returns
    -------
    pd.Series
        Series containing the number of unique color groups found across the
        selected columns for each row.

    Raises
    ------
    KeyError
        If any column listed in ``columns`` is not found in the dataframe.

    Notes
    -----
    Missing values are ignored. Empty strings are also ignored after splitting
    comma-separated values.

    This function does not create binary flags for specific color groups. For
    NFEI-style produce color diversity scoring, use
    :func:`add_produce_color_diversity`.

    Examples
    --------
    Count unique colors across fruit and vegetable color columns:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "fruit_colors": ["Red, Yellow_Orange", "Purple_Blue"],
    ...         "vegetable_colors": ["Green_other", "Red, Green_other"],
    ...     }
    ... )
    >>> result = nfei.count_unique_colors_in_columns(
    ...     df,
    ...     columns=["fruit_colors", "vegetable_colors"],
    ... )
    """
    
    missing_cols = [col for col in columns if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required column(s): {missing_cols}")

    unique_counts = []

    for _, row in df[columns].iterrows():
        unique_colors = set()

        for col in columns:
            value = row[col]

            if pd.notna(value):
                colors = [
                    color.strip()
                    for color in str(value).split(",")
                    if color.strip() != ""
                ]
                unique_colors.update(colors)

        unique_counts.append(len(unique_colors))

    return pd.Series(unique_counts, index=df.index, name=output_col)


def color_exists(
    row: pd.Series,
    color: str,
) -> int:
    """
    Check whether a color group exists across a row.

    This helper function scans all string values in a pandas Series and returns
    a binary indicator showing whether a specified color group is present. It is
    used internally by :func:`add_produce_color_diversity` to create binary
    color-group flags.

    The search is case-insensitive and supports comma-separated color values
    within cells.

    Parameters
    ----------
    row:
        A pandas Series, usually representing one row of selected color columns.

    color:
        Color group to search for. Leading and trailing spaces are ignored, and
        matching is case-insensitive.

    Returns
    -------
    int
        ``1`` if the color group is found in any string cell in the row,
        otherwise ``0``.

    Notes
    -----
    Non-string values are ignored. Missing values are ignored.

    This function is mainly exposed for users who need to build custom color
    diversity workflows. Most users should use
    :func:`add_produce_color_diversity` directly.

    Examples
    --------
    Check whether a color exists in a row with comma-separated values:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> row = pd.Series(
    ...     {
    ...         "fruit_colors": "Red, Yellow_Orange",
    ...         "vegetable_colors": "Green_other",
    ...     }
    ... )
    >>> nfei.color_exists(row, "Red")
    1

    Check for a color that is not present:

    >>> nfei.color_exists(row, "Purple_Blue")
    0
    """
    
    target_color = color.strip().lower()

    for value in row:
        if isinstance(value, str):
            colors = [
                item.strip().lower()
                for item in value.split(",")
                if item.strip() != ""
            ]

            if target_color in colors:
                return 1

    return 0


def add_produce_color_diversity(
    df: pd.DataFrame,
    color_cols: list[str],
    color_groups: list[str] | None = None,
    output_col: str = "overall_color",
    fillna_value: int | float = 0,
    include_color_flags: bool = True,
    flag_col_suffix: str = "_color",
) -> pd.DataFrame:
    
    """
    This function computes the produce color diversity component used in the
    NFEI workflow. It scans user-specified produce color columns for defined
    color groups and creates a score representing the number of color groups
    available for each observation.

    By default, the function uses the six NFEI produce color groups:

    - ``White_Brown``
    - ``Yellow_Orange``
    - ``Green_other``
    - ``Dark_leafy_green``
    - ``Red``
    - ``Purple_Blue``

    These color groups are used to summarize fruit and vegetable diversity
    beyond food-group counts alone. In the NFEI workflow, produce color
    diversity complements healthy food diversity by capturing variation in
    fruit and vegetable availability.

    Parameters
    ----------
    df:
        Input dataframe.

    color_cols:
        List of columns containing produce color values. Values may be single
        color names or comma-separated color names.

    color_groups:
        Optional list of color groups to search for. If None, the default NFEI
        color groups are used.

    output_col:
        Name of the output produce color diversity score. The default is
        ``"overall_color"``.

    fillna_value:
        Value used to replace missing output values before converting the final
        score to integer.

    include_color_flags:
        If True, binary flag columns are retained for each color group. If
        False, only the final color diversity score is retained.

    flag_col_suffix:
        Suffix added to each color group name when creating binary color flag
        columns. The default is ``"_color"``.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the produce color diversity score
        added. If ``include_color_flags=True``, binary color flag columns are
        also included.

    Raises
    ------
    KeyError
        If any column listed in ``color_cols`` is not found in the dataframe.

    ValueError
        If ``color_groups`` is an empty list.

    Notes
    -----
    Input color values may be stored as comma-separated strings, for example
    ``"Red, Yellow_Orange"``.

    Color matching is case-insensitive because the internal helper function
    :func:`color_exists` lowercases values before comparison. However, output
    flag column names preserve the spelling of the color group labels supplied
    in ``color_groups``.

    The final score counts how many color groups are present at least once
    across the selected columns. It does not count the number of individual food
    items.

    Examples
    --------
    Standard use with the default NFEI color groups:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "fruit_colors": ["Red, Yellow_Orange", "Purple_Blue"],
    ...         "vegetable_colors": ["Green_other", "Dark_leafy_green, Red"],
    ...     }
    ... )
    >>> result = nfei.add_produce_color_diversity(
    ...     df,
    ...     color_cols=["fruit_colors", "vegetable_colors"],
    ...     output_col="overall_color",
    ... )

    Return only the final color diversity score:

    >>> result = nfei.add_produce_color_diversity(
    ...     df,
    ...     color_cols=["fruit_colors", "vegetable_colors"],
    ...     include_color_flags=False,
    ... )

    Use a custom set of color groups:

    >>> result = nfei.add_produce_color_diversity(
    ...     df,
    ...     color_cols=["fruit_colors", "vegetable_colors"],
    ...     color_groups=["Red", "Green_other", "Purple_Blue"],
    ...     output_col="custom_color_score",
    ... )
    """
    
    missing_cols = [col for col in color_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required color column(s): {missing_cols}")

    if color_groups is None:
        color_groups = DEFAULT_COLOR_GROUPS.copy()

    if len(color_groups) == 0:
        raise ValueError("color_groups must contain at least one color.")

    new_df = df.copy()
    flag_cols = []

    for color in color_groups:
        clean_color_name = color.strip()
        flag_col = f"{clean_color_name}{flag_col_suffix}"

        new_df[flag_col] = new_df[color_cols].apply(
            color_exists,
            color=clean_color_name,
            axis=1,
        )

        flag_cols.append(flag_col)

    new_df[output_col] = new_df[flag_cols].sum(axis=1).fillna(fillna_value).astype(int)

    if not include_color_flags:
        new_df = new_df.drop(columns=flag_cols)

    return new_df