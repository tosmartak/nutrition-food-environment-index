from __future__ import annotations

import pandas as pd

# The required food groups for the Market-Level Diversity Score (MLDS)
# are based on the Minimum Dietary Diversity for Women food group structure.
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
    Add a Market-Level Diversity Score.

    This function computes the Market-Level Diversity Score (MLDS), a
    vendor-level food diversity indicator used in the NFEI workflow. It counts
    how many of the 10 required food groups are available for each observation.

    The food group structure follows the logic of the Minimum Dietary Diversity
    for Women framework, but is applied to market or vendor-level food
    availability data rather than individual dietary intake data.

    The required food groups are:

    - ``grains_roots_tubers``
    - ``legumes_pulses``
    - ``nuts_seeds``
    - ``dairy``
    - ``meat_poultry_fish``
    - ``eggs``
    - ``dark_green_leafy_vegetables``
    - ``vitamin_a_rich_fruits``
    - ``other_vegetables``
    - ``other_fruits``

    Users must explicitly map each required food group to the corresponding
    column or columns in their dataframe. If a food group is mapped to multiple
    columns, the group is scored as 1 when at least one mapped column has a
    value greater than zero.

    Parameters
    ----------
    df:
        Input dataframe.

    food_group_cols:
        Dictionary mapping each required food group to one dataframe column or
        a list of dataframe columns. The dictionary must contain exactly the 10
        required MLDS food group keys.

    output_col:
        Name of the output MLDS column. The default is ``"mlds"``.

    fillna_value:
        Value used to replace missing values in mapped food availability
        columns before calculating the score.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the MLDS column added.

    Raises
    ------
    KeyError
        If any required MLDS food group is missing, if unknown food group keys
        are provided, or if any mapped dataframe column is not found.

    ValueError
        If a food group is mapped to an empty list.

    TypeError
        If a food group is not mapped to either a column name or a list of
        column names.

    Notes
    -----
    The output score ranges from 0 to 10, where higher values indicate that a
    vendor or market observation offers more of the required food groups.

    Missing values in mapped food columns are filled using ``fillna_value``
    before scoring. By default, missing values are treated as 0.

    This function does not perform spatial aggregation. To construct
    environment-level diversity indicators, compute relevant binary food group
    columns first and then use a spatial aggregation function such as
    :func:`nfei.features_proximity_agg`.

    Examples
    --------
    Standard use with one or more columns mapped to each food group:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "grains": [1, 1],
    ...         "roots_tubers": [0, 1],
    ...         "legumes_pulses": [1, 0],
    ...         "nuts_seeds": [0, 1],
    ...         "dairy": [1, 0],
    ...         "flesh_meat": [1, 0],
    ...         "organ_meat": [0, 0],
    ...         "fish": [0, 1],
    ...         "egg": [1, 0],
    ...         "dark_green_veg": [0, 1],
    ...         "vita_rich_fruits": [1, 0],
    ...         "other_veg": [1, 1],
    ...         "other_fruits": [0, 1],
    ...     }
    ... )
    >>> food_group_cols = {
    ...     "grains_roots_tubers": ["grains", "roots_tubers"],
    ...     "legumes_pulses": "legumes_pulses",
    ...     "nuts_seeds": "nuts_seeds",
    ...     "dairy": "dairy",
    ...     "meat_poultry_fish": ["flesh_meat", "organ_meat", "fish"],
    ...     "eggs": "egg",
    ...     "dark_green_leafy_vegetables": "dark_green_veg",
    ...     "vitamin_a_rich_fruits": "vita_rich_fruits",
    ...     "other_vegetables": "other_veg",
    ...     "other_fruits": "other_fruits",
    ... }
    >>> result = nfei.add_market_level_diversity_score(
    ...     df,
    ...     food_group_cols=food_group_cols,
    ... )

    Use a custom output column name:

    >>> result = nfei.add_market_level_diversity_score(
    ...     df,
    ...     food_group_cols=food_group_cols,
    ...     output_col="vendor_healthy_food_diversity",
    ... )
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
    This utility function counts the number of available items across a list of
    binary or numeric columns. It is useful when several item-level variables
    need to be summarized into a single count indicator.

    In the NFEI workflow, this function is used internally by
    :func:`add_unhealthy_food_count` to count unhealthy beverage and snack
    availability before combining both categories into a total unhealthy food
    count.

    Parameters
    ----------
    df:
        Input dataframe.

    cols:
        List of binary or numeric columns to count across each row.

    output_col:
        Name of the output count column.

    fillna_value:
        Value used to replace missing values in ``cols`` before counting. The
        default is 0.

    Returns
    -------
    pd.DataFrame
        Copy of the input dataframe with the item count column added.

    Raises
    ------
    KeyError
        If any column listed in ``cols`` is not found in the dataframe.

    Notes
    -----
    The function sums values across ``cols`` row-wise. For binary columns, the
    result represents the number of available items. For non-binary numeric
    columns, the result is the row-wise sum of the supplied values.

    Missing values are filled before summation using ``fillna_value``.

    Examples
    --------
    Count available snack items from binary columns:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "biscuits": [1, 0],
    ...         "cookies": [1, 1],
    ...         "ice_cream": [0, 1],
    ...     }
    ... )
    >>> result = nfei.count_available_items(
    ...     df,
    ...     cols=["biscuits", "cookies", "ice_cream"],
    ...     output_col="snack_count",
    ... )
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
    This function constructs the unhealthy food exposure indicator used in the
    NFEI workflow. It counts selected unhealthy beverage items and selected
    unhealthy snack items separately, merges both counts by an identifier column,
    and then creates a total unhealthy food count.

    The function is designed for survey structures where beverage and snack
    availability may be stored in separate dataframes, such as separate repeat
    groups or separately cleaned item tables.

    Parameters
    ----------
    beverage_df:
        Dataframe containing the identifier column and unhealthy beverage item
        columns.

    snack_df:
        Dataframe containing the identifier column and unhealthy snack item
        columns.

    beverage_cols:
        List of binary or numeric beverage columns to count.

    snack_cols:
        List of binary or numeric snack columns to count.

    id_col:
        Identifier column used to merge beverage and snack counts. The default
        is ``"survey_id"``.

    beverage_count_col:
        Name of the output beverage count column. The default is
        ``"unhealthy_bev_count"``.

    snack_count_col:
        Name of the output snack count column. The default is
        ``"unhealthy_snack_count"``.

    output_col:
        Name of the total unhealthy food count column. The default is
        ``"unhealthy_food_count"``.

    Returns
    -------
    pd.DataFrame
        Dataframe containing the identifier column, unhealthy beverage count,
        unhealthy snack count, and total unhealthy food count.

    Raises
    ------
    KeyError
        If ``id_col`` is not found in either ``beverage_df`` or ``snack_df``, or
        if any column listed in ``beverage_cols`` or ``snack_cols`` is missing.

    Notes
    -----
    Beverage and snack counts are merged using an outer join. This preserves
    identifiers that appear in only one of the two input dataframes. Missing
    counts after the merge are filled with 0 before calculating the total count.

    The total unhealthy food count is calculated as:

    ``unhealthy beverage count + unhealthy snack count``

    Higher values represent greater availability of selected unhealthy foods.
    In an NFEI-style composite score, this indicator is typically inverted
    during scaling so that higher scaled values represent healthier food
    environments.

    Examples
    --------
    Count unhealthy beverages and snacks from separate item tables:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> beverage_df = pd.DataFrame(
    ...     {
    ...         "survey_id": [1, 2],
    ...         "alcoholic_beverages": [1, 0],
    ...         "energy_drinks": [1, 0],
    ...         "sweetened_beverages_fruit_juices": [0, 1],
    ...     }
    ... )
    >>> snack_df = pd.DataFrame(
    ...     {
    ...         "survey_id": [1, 2],
    ...         "biscuits": [1, 0],
    ...         "cakes_pastries": [1, 0],
    ...         "candies": [0, 1],
    ...         "cookies": [1, 0],
    ...         "sweets": [1, 1],
    ...     }
    ... )
    >>> result = nfei.add_unhealthy_food_count(
    ...     beverage_df=beverage_df,
    ...     snack_df=snack_df,
    ...     beverage_cols=[
    ...         "alcoholic_beverages",
    ...         "energy_drinks",
    ...         "sweetened_beverages_fruit_juices",
    ...     ],
    ...     snack_cols=[
    ...         "biscuits",
    ...         "cakes_pastries",
    ...         "candies",
    ...         "cookies",
    ...         "sweets",
    ...     ],
    ...     id_col="survey_id",
    ... )

    Use custom output column names:

    >>> result = nfei.add_unhealthy_food_count(
    ...     beverage_df=beverage_df,
    ...     snack_df=snack_df,
    ...     beverage_cols=[
    ...         "alcoholic_beverages",
    ...         "energy_drinks",
    ...         "sweetened_beverages_fruit_juices",
    ...     ],
    ...     snack_cols=[
    ...         "biscuits",
    ...         "cakes_pastries",
    ...         "candies",
    ...         "cookies",
    ...         "sweets",
    ...     ],
    ...     beverage_count_col="bev_count",
    ...     snack_count_col="snack_count",
    ...     output_col="total_unhealthy_items",
    ... )
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