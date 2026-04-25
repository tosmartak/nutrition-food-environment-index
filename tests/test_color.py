import pandas as pd
import pytest

from nfei.color import (
    add_produce_color_diversity,
    color_exists,
    count_unique_colors_in_columns,
)


def test_count_unique_colors_in_columns_matches_notebook_logic():
    df = pd.DataFrame(
        {
            "apple_color": ["Red", "Green_other, Red"],
            "banana_color": ["Yellow_Orange", None],
            "grapes_color": ["Purple_Blue, Green_other", "Purple_Blue"],
        }
    )

    result = count_unique_colors_in_columns(
        df,
        columns=["apple_color", "banana_color", "grapes_color"],
    )

    assert result.tolist() == [4, 3]


def test_color_exists_returns_one_when_color_is_present():
    row = pd.Series(
        {
            "apple_color": "Red",
            "banana_color": "Yellow_Orange, White_Brown",
        }
    )

    assert color_exists(row, "White_Brown") == 1


def test_color_exists_returns_zero_when_color_is_absent():
    row = pd.Series(
        {
            "apple_color": "Red",
            "banana_color": "Yellow_Orange",
        }
    )

    assert color_exists(row, "Purple_Blue") == 0


def test_add_produce_color_diversity_adds_flags_and_overall_score():
    df = pd.DataFrame(
        {
            "apple_color": ["Red", "Green_other"],
            "banana_color": ["Yellow_Orange", None],
            "grapes_color": ["Purple_Blue", "Purple_Blue, Red"],
        }
    )

    result = add_produce_color_diversity(
        df,
        color_cols=["apple_color", "banana_color", "grapes_color"],
    )

    assert result["Red_color"].tolist() == [1, 1]
    assert result["Yellow_Orange_color"].tolist() == [1, 0]
    assert result["Green_other_color"].tolist() == [0, 1]
    assert result["Purple_Blue_color"].tolist() == [1, 1]
    assert result["overall_color"].tolist() == [3, 3]


def test_add_produce_color_diversity_can_return_only_overall_score():
    df = pd.DataFrame(
        {
            "apple_color": ["Red"],
            "banana_color": ["Yellow_Orange"],
        }
    )

    result = add_produce_color_diversity(
        df,
        color_cols=["apple_color", "banana_color"],
        include_color_flags=False,
    )

    assert "overall_color" in result.columns
    assert "Red_color" not in result.columns
    assert result["overall_color"].iloc[0] == 2


def test_add_produce_color_diversity_raises_error_for_missing_columns():
    df = pd.DataFrame({"apple_color": ["Red"]})

    with pytest.raises(KeyError):
        add_produce_color_diversity(
            df,
            color_cols=["apple_color", "banana_color"],
        )


def test_add_produce_color_diversity_raises_error_for_empty_color_groups():
    df = pd.DataFrame({"apple_color": ["Red"]})

    with pytest.raises(ValueError):
        add_produce_color_diversity(
            df,
            color_cols=["apple_color"],
            color_groups=[],
        )