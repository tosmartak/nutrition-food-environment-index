from __future__ import annotations

import pandas as pd

# The required food groups for the Market-Level Diversity Score (MLDS) are based on the Minimum Dietary
REQUIRED_MLDS_GROUPS = [
    "grains_roots_tubers",
    "legumes_pulses",
    "nuts_seeds",
    "dairy",
    "meat_poultry_fish",
    "eggs",
    "dark_green_leafy_vegetables",
    "vitamin_a_rich_fruits",
    "other_vegetables",
    "other_fruits",
]

def add_market_level_diversity_score(
    df: pd.DataFrame,
    food_group_cols: dict[str, str | list[str]],
    output_col: str = "mlds",
    fillna_value: int | float = 0,
) -> pd.DataFrame:
    """
    Add a Market-Level Diversity Score (MLDS) to a dataframe.

    MLDS counts the availability of 10 food groups per observation. The food
    group structure mirrors the Minimum Dietary Diversity for Women framework,
    but is applied to market/vendor-level food availability data rather than
    individual dietary intake data.

    Users must map each required food group to the corresponding column or
    columns in their dataframe. If a food group is mapped to multiple columns,
    the group is scored as 1 when any of those columns is available.

    Required food groups
    --------------------
    - grains_roots_tubers
    - legumes_pulses
    - nuts_seeds
    - dairy
    - meat_poultry_fish
    - eggs
    - dark_green_leafy_vegetables
    - vitamin_a_rich_fruits
    - other_vegetables
    - other_fruits

    Parameters
    ----------
    df:
        Input dataframe.

    food_group_cols:
        Dictionary mapping each required food group to one dataframe column or
        a list of dataframe columns.

    output_col:
        Name of the MLDS output column.

    fillna_value:
        Value used to replace missing values before calculating availability.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with one new MLDS column added.
    """
    provided_groups = set(food_group_cols.keys())
    required_groups = set(REQUIRED_MLDS_GROUPS)

    missing_groups = sorted(required_groups - provided_groups)
    extra_groups = sorted(provided_groups - required_groups)

    if missing_groups:
        raise KeyError(f"Missing required MLDS food group(s): {missing_groups}")

    if extra_groups:
        raise KeyError(f"Unknown MLDS food group(s): {extra_groups}")

    mapped_cols = []
    for group, cols in food_group_cols.items():
        if isinstance(cols, str):
            mapped_cols.append(cols)
        elif isinstance(cols, list) and all(isinstance(col, str) for col in cols):
            if len(cols) == 0:
                raise ValueError(f"Food group '{group}' was mapped to an empty list.")
            mapped_cols.extend(cols)
        else:
            raise TypeError(
                f"Food group '{group}' must be mapped to a column name "
                "or a list of column names."
            )

    missing_cols = sorted(set(mapped_cols) - set(df.columns))
    if missing_cols:
        raise KeyError(f"Mapped dataframe column(s) not found: {missing_cols}")

    new_df = df.copy()
    new_df[mapped_cols] = new_df[mapped_cols].astype("Float64").fillna(fillna_value)

    group_scores = pd.DataFrame(index=new_df.index)

    for group, cols in food_group_cols.items():
        if isinstance(cols, str):
            group_scores[group] = (new_df[cols] > 0).astype(int)
        else:
            group_scores[group] = (new_df[cols].sum(axis=1) > 0).astype(int)

    new_df[output_col] = group_scores[REQUIRED_MLDS_GROUPS].sum(axis=1).astype(int)

    return new_df

def count_available_items(
    df: pd.DataFrame,
    cols: list[str],
    output_col: str,
    fillna_value: int | float = 0,
) -> pd.DataFrame:
    """
    Count available items across a list of binary or numeric columns.
    """
    missing_cols = [col for col in cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required column(s): {missing_cols}")

    new_df = df.copy()
    new_df[cols] = new_df[cols].fillna(fillna_value)
    new_df[output_col] = new_df[cols].sum(axis=1).astype(int)

    return new_df

def add_unhealthy_food_count(
    beverage_df: pd.DataFrame,
    snack_df: pd.DataFrame,
    beverage_cols: list[str],
    snack_cols: list[str],
    id_col: str = "survey_id",
    beverage_count_col: str = "unhealthy_bev_count",
    snack_count_col: str = "unhealthy_snack_count",
    output_col: str = "unhealthy_food_count",
) -> pd.DataFrame:
    """
    Create unhealthy beverage, snack, and total unhealthy food counts.

    Beverage and snack tables are counted separately, merged by ID, missing
    values are replaced with zero, and the total unhealthy food count is
    calculated.
    """

    if id_col not in beverage_df.columns:
        raise KeyError(f"Column '{id_col}' was not found in beverage_df.")

    if id_col not in snack_df.columns:
        raise KeyError(f"Column '{id_col}' was not found in snack_df.")

    beverage_counts = count_available_items(
        beverage_df,
        cols=beverage_cols,
        output_col=beverage_count_col,
    )[[id_col, beverage_count_col]]

    snack_counts = count_available_items(
        snack_df,
        cols=snack_cols,
        output_col=snack_count_col,
    )[[id_col, snack_count_col]]

    unhealthy_df = beverage_counts.merge(snack_counts, on=id_col, how="outer")
    unhealthy_df = unhealthy_df.fillna(0)

    unhealthy_df[beverage_count_col] = unhealthy_df[beverage_count_col].astype(int)
    unhealthy_df[snack_count_col] = unhealthy_df[snack_count_col].astype(int)

    unhealthy_df[output_col] = unhealthy_df[
        [beverage_count_col, snack_count_col]
    ].sum(axis=1).astype(int)

    return unhealthy_df