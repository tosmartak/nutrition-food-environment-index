# Methodology

The `nfei` package implements reusable components for constructing Nutrition-Sensitive Food Environment Index indicators. It is based on the N-FEI methodology described in: [https://doi.org/10.55845/jos-2025-1116](https://doi.org/10.55845/jos-2025-1116)

## Indicator workflow

A typical N-FEI workflow follows these stages:

1. Start with raw vendor, food availability, sanitation, and spatial data.
2. Validate coordinate and required input columns.
3. Compute individual food environment indicators.
4. Use spatial aggregation where indicators require environmental exposure around vendors.
5. Scale indicators to a common range.
6. Invert negative indicators where higher raw values represent poorer food environments.
7. Aggregate selected normalized indicators into a composite score.
8. Compute final NFEI score

## Indicator families

### Food diversity

Food diversity indicators measure the availability of food groups at the vendor or market-environment level. In this package, `add_market_level_diversity_score` computes availability across 10 required food groups.

### Produce color diversity

Produce color diversity captures fruit and vegetable color availability using six default color groups. This is implemented through `add_produce_color_diversity`.

### Vendor availability

Vendor availability reflects temporal access to vendors across the day and week. This is implemented through:

- `add_daily_availability`
- `add_weekly_availability`
- `add_vendor_availability`

### Vendor density and distribution

Vendor density indicators relate vendor counts to population and land area. These are implemented through:

- `estimate_population_from_radius`
- `add_vendor_density`

### Spatial exposure

Some N-FEI indicators require considering what is available around a vendor, not only at the vendor. Spatial aggregation is implemented through:

- `calc_distance`
- `features_proximity_agg`

### Scaling and inversion

Indicators are often aligned to a common 0–10 scale before aggregation. Negative indicators, such as unhealthy food exposure, can be inverted using `create_linear_scale`.

### Validation

Spatial and numeric quality checks are supported through:

- `mad_based_outlier`
- `fix_spatial_outliers`

## Composite score construction

The package does not force a single black-box index calculation. Instead, it gives users transparent components that can be combined according to their study design.

A simple composite score can be calculated as:

```python
indicator_cols = [
    "mlds_scaled",
    "mlds_scaled_50m",
    "overall_color_scaled",
    "overall_color_scaled_50m",
    "unhealthy_food_inverted",
    "vendor_availability_scaled",
    "vendor_per_pop_scaled",
    "vendor_per_sqkm_scaled",
    "access_to_sanitatn"
]

df["nfei_score"] = df[indicator_cols].mean(axis=1)
```