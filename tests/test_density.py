import pytest
import pandas as pd

from nfei.density import add_vendor_density, estimate_population_from_radius


def test_estimate_population_from_radius_matches_notebook_logic():
    result = estimate_population_from_radius(
        population=738444,
        land_area_sqkm=79,
        radius_km=1,
    )

    assert result["area_covered_sqkm"] == 3.14
    assert result["estimated_population"] == 29366


def test_estimate_population_from_radius_without_rounding():
    result = estimate_population_from_radius(
        population=618709,
        land_area_sqkm=1770,
        radius_km=1,
        round_area=None,
        round_population=None,
    )

    assert result["area_covered_sqkm"] > 3.141
    assert result["estimated_population"] > 1097


def test_estimate_population_from_radius_raises_error_for_invalid_inputs():
    with pytest.raises(ValueError):
        estimate_population_from_radius(
            population=0,
            land_area_sqkm=79,
            radius_km=1,
        )

    with pytest.raises(ValueError):
        estimate_population_from_radius(
            population=738444,
            land_area_sqkm=0,
            radius_km=1,
        )

    with pytest.raises(ValueError):
        estimate_population_from_radius(
            population=738444,
            land_area_sqkm=79,
            radius_km=0,
        )


def test_add_vendor_density_matches_original_logic():
    df = pd.DataFrame(
        {
            "ward": ["Viwandani", "Viwandani", "Viwandani", "Kalonzoni"],
            "vendor_type": ["shop", "shop", "kiosk", "shop"],
            "Population": [43070, 43070, 43070, 8770],
            "Land_area_sqkm": [5, 5, 5, 32.6],
        }
    )

    result = add_vendor_density(
        df,
        group_col="ward",
        vendor_type_col="vendor_type",
        population_col="Population",
        land_area_col="Land_area_sqkm",
    )

    viwandani_shop = result[
        (result["ward"] == "Viwandani") & (result["vendor_type"] == "shop")
    ]

    assert viwandani_shop["vendor_type_pop"].tolist() == [2, 2]
    assert viwandani_shop["vendor_type_per_pop"].iloc[0] == 2 / 43070
    assert viwandani_shop["vendor_type_per_sqkm"].iloc[0] == 2 / 5


def test_add_vendor_density_with_optional_rate_per():
    df = pd.DataFrame(
        {
            "ward": ["A", "A", "A"],
            "vendor_type": ["shop", "shop", "kiosk"],
            "Population": [1000, 1000, 1000],
            "Land_area_sqkm": [2, 2, 2],
        }
    )

    result = add_vendor_density(
        df,
        group_col="ward",
        vendor_type_col="vendor_type",
        population_col="Population",
        land_area_col="Land_area_sqkm",
        rate_per=1000,
    )

    shop_rows = result[result["vendor_type"] == "shop"]

    assert shop_rows["vendor_type_pop"].iloc[0] == 2
    assert shop_rows["vendor_type_per_pop"].iloc[0] == 2 / 1000
    assert shop_rows["vendor_type_per_pop_per_1000"].iloc[0] == 2


def test_add_vendor_density_raises_error_for_missing_columns():
    df = pd.DataFrame(
        {
            "ward": ["A"],
            "vendor_type": ["shop"],
        }
    )

    with pytest.raises(KeyError):
        add_vendor_density(
            df,
            group_col="ward",
            vendor_type_col="vendor_type",
            population_col="Population",
            land_area_col="Land_area_sqkm",
        )


def test_add_vendor_density_raises_error_for_invalid_population_or_area():
    df_bad_population = pd.DataFrame(
        {
            "ward": ["A"],
            "vendor_type": ["shop"],
            "Population": [0],
            "Land_area_sqkm": [2],
        }
    )

    with pytest.raises(ValueError):
        add_vendor_density(
            df_bad_population,
            group_col="ward",
            vendor_type_col="vendor_type",
            population_col="Population",
            land_area_col="Land_area_sqkm",
        )

    df_bad_area = pd.DataFrame(
        {
            "ward": ["A"],
            "vendor_type": ["shop"],
            "Population": [1000],
            "Land_area_sqkm": [0],
        }
    )

    with pytest.raises(ValueError):
        add_vendor_density(
            df_bad_area,
            group_col="ward",
            vendor_type_col="vendor_type",
            population_col="Population",
            land_area_col="Land_area_sqkm",
        )