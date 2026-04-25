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
    Count unique produce colors across selected columns for each observation.

    Color values can be comma-separated strings, as used in the original NFEI
    notebooks.
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
    Check whether a specific color exists across a dataframe row.

    Returns 1 if the color exists in any string cell in the row, otherwise 0.
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
    Add produce color diversity indicators to a dataframe.

    This mirrors the NFEI notebook logic where produce color columns are scanned
    for six color groups and the final color diversity score is calculated as
    the number of color groups available per observation.

    Parameters
    ----------
    df:
        Input dataframe.

    color_cols:
        Columns containing produce color values. Values may be comma-separated.

    color_groups:
        Color groups to search for. If None, the six NFEI color groups are used:
        White_Brown, Yellow_Orange, Green_other, Dark_leafy_green, Red,
        Purple_Blue.

    output_col:
        Name of the final produce color diversity score.

    fillna_value:
        Value used to replace missing output values.

    include_color_flags:
        If True, binary columns are created for each color group.

    flag_col_suffix:
        Suffix added to each color group name when creating binary color flags.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with color diversity indicators added.
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