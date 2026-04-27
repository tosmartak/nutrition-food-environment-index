import numpy as np
import pandas as pd
import pytest

from nfei.availability import (
    add_daily_availability,
    add_vendor_availability,
    add_weekly_availability,
)


TIME_COLS = {
    "morning": "available_morning",
    "afternoon": "available_afternoon",
    "evening": "available_evening",
    "night": "available_night",
}

DAY_COLS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def test_add_daily_availability_matches_notebook_logic():
    df = pd.DataFrame(
        {
            "vendor_allday": [1, 0, 0],
            "available_morning": [0, 1, 1],
            "available_afternoon": [0, 1, 0],
            "available_evening": [0, 0, 1],
            "available_night": [0, 0, 1],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col="vendor_allday",
    )

    assert result["perc_daily_avail"].tolist() == [100, 60, 70]


def test_add_daily_availability_accepts_custom_weights():
    df = pd.DataFrame(
        {
            "vendor_allday": [0],
            "available_morning": [1],
            "available_afternoon": [1],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col="vendor_allday",
        time_weights={
            "morning": 25,
            "afternoon": 25,
            "evening": 25,
            "night": 25,
        },
    )

    assert result["perc_daily_avail"].iloc[0] == 50


def test_add_daily_availability_works_without_all_day_col():
    df = pd.DataFrame(
        {
            "available_morning": [1],
            "available_afternoon": [1],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col=None,
    )

    assert result["perc_daily_avail"].iloc[0] == 60


def test_add_daily_availability_allows_missing_time_cols_when_all_day_is_one():
    df = pd.DataFrame(
        {
            "vendor_allday": [1],
            "available_morning": [np.nan],
            "available_afternoon": [np.nan],
            "available_evening": [np.nan],
            "available_night": [np.nan],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col="vendor_allday",
    )

    assert result["perc_daily_avail"].iloc[0] == 100


def test_add_daily_availability_raises_for_missing_time_cols_when_all_day_is_not_one():
    df = pd.DataFrame(
        {
            "vendor_allday": [0],
            "available_morning": [1],
            "available_afternoon": [np.nan],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    with pytest.raises(ValueError):
        add_daily_availability(
            df,
            time_cols=TIME_COLS,
            all_day_col="vendor_allday",
        )


def test_add_daily_availability_raises_for_missing_time_cols_without_all_day_col():
    df = pd.DataFrame(
        {
            "available_morning": [1],
            "available_afternoon": [np.nan],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    with pytest.raises(ValueError):
        add_daily_availability(
            df,
            time_cols=TIME_COLS,
            all_day_col=None,
        )


def test_add_daily_availability_can_fill_missing_time_cols():
    df = pd.DataFrame(
        {
            "available_morning": [1],
            "available_afternoon": [np.nan],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col=None,
        missing_policy="fill",
    )

    assert result["perc_daily_avail"].iloc[0] == 30


def test_add_daily_availability_raises_error_for_mismatched_weight_keys():
    df = pd.DataFrame(
        {
            "vendor_allday": [0],
            "available_morning": [1],
            "available_afternoon": [1],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    with pytest.raises(ValueError):
        add_daily_availability(
            df,
            time_cols=TIME_COLS,
            all_day_col="vendor_allday",
            time_weights={"morning": 30},
        )


def test_add_daily_availability_raises_error_for_missing_column():
    df = pd.DataFrame(
        {
            "vendor_allday": [0],
            "available_morning": [1],
        }
    )

    with pytest.raises(KeyError):
        add_daily_availability(
            df,
            time_cols=TIME_COLS,
            all_day_col="vendor_allday",
        )


def test_add_daily_availability_raises_for_invalid_missing_policy():
    df = pd.DataFrame(
        {
            "available_morning": [1],
            "available_afternoon": [1],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    with pytest.raises(ValueError):
        add_daily_availability(
            df,
            time_cols=TIME_COLS,
            missing_policy="invalid",
        )


def test_add_weekly_availability_matches_notebook_logic():
    df = pd.DataFrame(
        {
            "vendor_allweek": [1, 0, 0],
            "monday": [0, 1, 1],
            "tuesday": [0, 1, 1],
            "wednesday": [0, 1, 1],
            "thursday": [0, 0, 1],
            "friday": [0, 0, 1],
            "saturday": [0, 0, 0],
            "sunday": [0, 0, 0],
        }
    )

    result = add_weekly_availability(
        df,
        day_cols=DAY_COLS,
        all_week_col="vendor_allweek",
        round_result=True,
    )

    assert result["perc_weekly_avail"].tolist() == [100, 42, 71]


def test_add_weekly_availability_works_without_all_week_col():
    df = pd.DataFrame(
        {
            "monday": [1],
            "tuesday": [1],
            "wednesday": [1],
            "thursday": [0],
            "friday": [0],
            "saturday": [0],
            "sunday": [0],
        }
    )

    result = add_weekly_availability(
        df,
        day_cols=DAY_COLS,
        all_week_col=None,
        round_result=True,
    )

    assert result["perc_weekly_avail"].iloc[0] == 42


def test_add_weekly_availability_requires_day_cols_to_match_days_in_week():
    df = pd.DataFrame({"monday": [1]})

    with pytest.raises(ValueError):
        add_weekly_availability(
            df,
            day_cols=["monday"],
            all_week_col=None,
        )


def test_add_weekly_availability_allows_missing_day_cols_when_all_week_is_one():
    df = pd.DataFrame(
        {
            "vendor_allweek": [1],
            "monday": [np.nan],
            "tuesday": [np.nan],
            "wednesday": [np.nan],
            "thursday": [np.nan],
            "friday": [np.nan],
            "saturday": [np.nan],
            "sunday": [np.nan],
        }
    )

    result = add_weekly_availability(
        df,
        day_cols=DAY_COLS,
        all_week_col="vendor_allweek",
    )

    assert result["perc_weekly_avail"].iloc[0] == 100


def test_add_weekly_availability_raises_for_missing_day_cols_when_all_week_is_not_one():
    df = pd.DataFrame(
        {
            "vendor_allweek": [0],
            "monday": [1],
            "tuesday": [1],
            "wednesday": [np.nan],
            "thursday": [0],
            "friday": [0],
            "saturday": [0],
            "sunday": [0],
        }
    )

    with pytest.raises(ValueError):
        add_weekly_availability(
            df,
            day_cols=DAY_COLS,
            all_week_col="vendor_allweek",
        )


def test_add_weekly_availability_raises_for_missing_day_cols_without_all_week_col():
    df = pd.DataFrame(
        {
            "monday": [1],
            "tuesday": [1],
            "wednesday": [np.nan],
            "thursday": [0],
            "friday": [0],
            "saturday": [0],
            "sunday": [0],
        }
    )

    with pytest.raises(ValueError):
        add_weekly_availability(
            df,
            day_cols=DAY_COLS,
            all_week_col=None,
        )


def test_add_weekly_availability_can_fill_missing_day_cols():
    df = pd.DataFrame(
        {
            "monday": [1],
            "tuesday": [1],
            "wednesday": [np.nan],
            "thursday": [0],
            "friday": [0],
            "saturday": [0],
            "sunday": [0],
        }
    )

    result = add_weekly_availability(
        df,
        day_cols=DAY_COLS,
        all_week_col=None,
        missing_policy="fill",
        round_result=True,
    )

    assert result["perc_weekly_avail"].iloc[0] == 28


def test_add_weekly_availability_raises_error_for_missing_day_col():
    df = pd.DataFrame(
        {
            "vendor_allweek": [1],
            "monday": [1],
            "tuesday": [1],
            "wednesday": [1],
            "thursday": [1],
            "friday": [1],
            "saturday": [1],
        }
    )

    with pytest.raises(KeyError):
        add_weekly_availability(
            df,
            day_cols=DAY_COLS,
            all_week_col="vendor_allweek",
        )


def test_add_weekly_availability_raises_error_for_invalid_days_in_week():
    df = pd.DataFrame({"vendor_allweek": [1], "monday": [1]})

    with pytest.raises(ValueError):
        add_weekly_availability(
            df,
            day_cols=["monday"],
            all_week_col="vendor_allweek",
            days_in_week=0,
        )


def test_add_weekly_availability_raises_for_invalid_missing_policy():
    df = pd.DataFrame(
        {
            "monday": [1],
            "tuesday": [1],
            "wednesday": [1],
            "thursday": [1],
            "friday": [1],
            "saturday": [1],
            "sunday": [1],
        }
    )

    with pytest.raises(ValueError):
        add_weekly_availability(
            df,
            day_cols=DAY_COLS,
            missing_policy="invalid",
        )


def test_add_vendor_availability_takes_mean_of_daily_and_weekly():
    df = pd.DataFrame(
        {
            "perc_daily_avail": [100, 60],
            "perc_weekly_avail": [100, 40],
        }
    )

    result = add_vendor_availability(df)

    assert result["perc_vendor_avail"].tolist() == [100, 50]


def test_add_vendor_availability_raises_error_for_missing_input_column():
    df = pd.DataFrame({"perc_daily_avail": [100]})

    with pytest.raises(KeyError):
        add_vendor_availability(df)


def test_functions_do_not_mutate_original_dataframe():
    df = pd.DataFrame(
        {
            "vendor_allday": [0],
            "available_morning": [1],
            "available_afternoon": [1],
            "available_evening": [0],
            "available_night": [0],
        }
    )

    result = add_daily_availability(
        df,
        time_cols=TIME_COLS,
        all_day_col="vendor_allday",
    )

    assert "perc_daily_avail" not in df.columns
    assert "perc_daily_avail" in result.columns