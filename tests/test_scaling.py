import pandas as pd
import pytest

from nfei.scaling import create_linear_scale


def test_create_linear_scale_basic():
    df = pd.DataFrame({"market_dds": [0, 3, 6]})

    result = create_linear_scale(
        df,
        col="market_dds",
        expected_max=6,
        min_scale=0,
        max_scale=10,
        var_title="market_dds_score",
    )

    assert result["market_dds_score"].tolist() == [0, 5, 10]


def test_create_linear_scale_with_inversion():
    df = pd.DataFrame({"constraints": [0, 3, 6]})

    result = create_linear_scale(
        df,
        col="constraints",
        expected_max=6,
        min_scale=0,
        max_scale=10,
        invert=True,
        var_title="constraint_score",
    )

    assert result["constraint_score"].tolist() == [10, 5, 0]


def test_create_linear_scale_uses_expected_max_adjustment():
    df = pd.DataFrame({"market_dds": [0, 3, 6]})

    result = create_linear_scale(
        df,
        col="market_dds",
        expected_max=12,
        min_scale=0,
        max_scale=10,
        var_title="market_dds_score",
    )

    assert result["market_dds_score"].tolist() == [0, 2.5, 5]


def test_create_linear_scale_raises_error_for_missing_column():
    df = pd.DataFrame({"x": [1, 2, 3]})

    with pytest.raises(KeyError):
        create_linear_scale(df, col="missing")


def test_create_linear_scale_raises_error_for_invalid_scale():
    df = pd.DataFrame({"x": [1, 2, 3]})

    with pytest.raises(ValueError):
        create_linear_scale(df, col="x", min_scale=10, max_scale=0)