import pandas as pd
import pytest

from nfei.diversity import (
    add_market_level_diversity_score,
    add_unhealthy_food_count,
    count_available_items,
)


BEVERAGE_COLS = [
    "alcoholic_beverages",
    "energy_drinks",
    "sweetened_beverages_fruit_juices",
]

SNACK_COLS = [
    "biscuits",
    "canned_fruits",
    "cakes_pastries",
    "candies",
    "cookies",
    "chocolates",
    "ice_cream",
    "pie",
    "sweets",
]


def valid_food_group_mapping():
    return {
        "grains_roots_tubers": ["grains", "roots_tubers"],
        "legumes_pulses": "legumes_pulses",
        "nuts_seeds": "nuts_seeds",
        "dairy": "dairy",
        "meat_poultry_fish": ["flesh_meat", "organ_meat", "fish"],
        "eggs": "egg",
        "dark_green_leafy_vegetables": "dark_green_veg",
        "vitamin_a_rich_fruits": "vita_rich_fruits",
        "other_vegetables": "other_veg",
        "other_fruits": "other_fruits",
    }


def test_add_market_level_diversity_score_with_mapping():
    df = pd.DataFrame(
        {
            "grains": [1, 0],
            "roots_tubers": [0, 1],
            "legumes_pulses": [1, 0],
            "nuts_seeds": [0, 1],
            "dairy": [1, 0],
            "flesh_meat": [1, 0],
            "organ_meat": [0, 0],
            "fish": [0, 1],
            "egg": [1, 0],
            "dark_green_veg": [0, 1],
            "vita_rich_fruits": [1, 0],
            "other_veg": [1, 1],
            "other_fruits": [0, 1],
        }
    )

    result = add_market_level_diversity_score(
        df,
        food_group_cols=valid_food_group_mapping(),
    )

    assert result["mlds"].tolist() == [7, 6]


def test_add_market_level_diversity_score_handles_na_as_zero():
    df = pd.DataFrame(
        {
            "grains": [1],
            "roots_tubers": [None],
            "legumes_pulses": [1],
            "nuts_seeds": [None],
            "dairy": [1],
            "flesh_meat": [None],
            "organ_meat": [0],
            "fish": [1],
            "egg": [1],
            "dark_green_veg": [0],
            "vita_rich_fruits": [1],
            "other_veg": [1],
            "other_fruits": [0],
        }
    )

    result = add_market_level_diversity_score(
        df,
        food_group_cols=valid_food_group_mapping(),
    )

    assert result["mlds"].iloc[0] == 7


def test_add_market_level_diversity_score_raises_error_for_missing_group():
    mapping = valid_food_group_mapping()
    mapping.pop("other_fruits")

    df = pd.DataFrame({"grains": [1]})

    with pytest.raises(KeyError):
        add_market_level_diversity_score(df, food_group_cols=mapping)


def test_add_market_level_diversity_score_raises_error_for_extra_group():
    mapping = valid_food_group_mapping()
    mapping["extra_group"] = "extra_col"

    df = pd.DataFrame({"grains": [1]})

    with pytest.raises(KeyError):
        add_market_level_diversity_score(df, food_group_cols=mapping)


def test_add_market_level_diversity_score_raises_error_for_missing_dataframe_column():
    df = pd.DataFrame(
        {
            "grains": [1],
            "roots_tubers": [0],
        }
    )

    with pytest.raises(KeyError):
        add_market_level_diversity_score(
            df,
            food_group_cols=valid_food_group_mapping(),
        )


def test_count_available_items_sums_columns():
    df = pd.DataFrame(
        {
            "biscuits": [1, 0],
            "cookies": [1, 1],
            "ice_cream": [0, 1],
        }
    )

    result = count_available_items(
        df,
        cols=["biscuits", "cookies", "ice_cream"],
        output_col="snack_count",
    )

    assert result["snack_count"].tolist() == [2, 2]


def test_add_unhealthy_food_count_matches_notebook_logic():
    beverage_df = pd.DataFrame(
        {
            "survey_id": [1, 2],
            "alcoholic_beverages": [1, 0],
            "energy_drinks": [1, 0],
            "sweetened_beverages_fruit_juices": [0, 1],
        }
    )

    snack_df = pd.DataFrame(
        {
            "survey_id": [1, 2],
            "biscuits": [1, 0],
            "canned_fruits": [0, 0],
            "cakes_pastries": [1, 0],
            "candies": [0, 1],
            "cookies": [1, 0],
            "chocolates": [0, 1],
            "ice_cream": [0, 0],
            "pie": [0, 0],
            "sweets": [1, 1],
        }
    )

    result = add_unhealthy_food_count(
        beverage_df,
        snack_df,
        beverage_cols=BEVERAGE_COLS,
        snack_cols=SNACK_COLS,
    )
    result = result.sort_values("survey_id").reset_index(drop=True)

    assert result["unhealthy_bev_count"].tolist() == [2, 1]
    assert result["unhealthy_snack_count"].tolist() == [4, 3]
    assert result["unhealthy_food_count"].tolist() == [6, 4]


def test_add_unhealthy_food_count_keeps_outer_merge_logic():
    beverage_df = pd.DataFrame(
        {
            "survey_id": [1],
            "alcoholic_beverages": [1],
            "energy_drinks": [0],
            "sweetened_beverages_fruit_juices": [1],
        }
    )

    snack_df = pd.DataFrame(
        {
            "survey_id": [2],
            "biscuits": [1],
            "canned_fruits": [0],
            "cakes_pastries": [0],
            "candies": [0],
            "cookies": [0],
            "chocolates": [0],
            "ice_cream": [0],
            "pie": [0],
            "sweets": [1],
        }
    )

    result = add_unhealthy_food_count(
        beverage_df,
        snack_df,
        beverage_cols=BEVERAGE_COLS,
        snack_cols=SNACK_COLS,
    )

    assert set(result["survey_id"]) == {1, 2}