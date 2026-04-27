"""
nfei: Nutrition Food Environment Index utilities.
"""

from nfei.availability import (
    add_daily_availability,
    add_vendor_availability,
    add_weekly_availability,
)
from nfei.color import (
    add_produce_color_diversity,
    color_exists,
    count_unique_colors_in_columns,
)
from nfei.density import (
    add_vendor_density,
    estimate_population_from_radius,
)
from nfei.diversity import (
    add_market_level_diversity_score,
    add_unhealthy_food_count,
    count_available_items,
)
from nfei.scaling import create_linear_scale
from nfei.spatial import (
    calc_distance,
    features_proximity_agg,
    haversine_vectorized,
)
from nfei.validation import (
    fix_spatial_outliers,
    mad_based_outlier,
)

__all__ = [
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
]