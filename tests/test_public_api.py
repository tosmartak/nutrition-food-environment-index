import nfei


def test_public_api_exposes_availability_functions():
    assert hasattr(nfei, "add_daily_availability")
    assert hasattr(nfei, "add_weekly_availability")
    assert hasattr(nfei, "add_vendor_availability")


def test_public_api_exposes_color_functions():
    assert hasattr(nfei, "add_produce_color_diversity")
    assert hasattr(nfei, "color_exists")
    assert hasattr(nfei, "count_unique_colors_in_columns")


def test_public_api_exposes_density_functions():
    assert hasattr(nfei, "add_vendor_density")
    assert hasattr(nfei, "estimate_population_from_radius")


def test_public_api_exposes_diversity_functions():
    assert hasattr(nfei, "add_market_level_diversity_score")
    assert hasattr(nfei, "add_unhealthy_food_count")
    assert hasattr(nfei, "count_available_items")


def test_public_api_exposes_scaling_functions():
    assert hasattr(nfei, "create_linear_scale")


def test_public_api_exposes_spatial_functions():
    assert hasattr(nfei, "calc_distance")
    assert hasattr(nfei, "features_proximity_agg")
    assert hasattr(nfei, "haversine_vectorized")


def test_public_api_exposes_validation_functions():
    assert hasattr(nfei, "fix_spatial_outliers")
    assert hasattr(nfei, "mad_based_outlier")


def test_public_api_all_contains_expected_functions():
    expected = {
        "add_daily_availability",
        "add_vendor_availability",
        "add_weekly_availability",
        "add_produce_color_diversity",
        "color_exists",
        "count_unique_colors_in_columns",
        "add_vendor_density",
        "estimate_population_from_radius",
        "add_market_level_diversity_score",
        "add_unhealthy_food_count",
        "count_available_items",
        "create_linear_scale",
        "calc_distance",
        "features_proximity_agg",
        "haversine_vectorized",
        "fix_spatial_outliers",
        "mad_based_outlier",
    }

    assert set(nfei.__all__) == expected