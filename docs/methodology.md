# Methodology

The `nfei` package implements reusable components for constructing Nutrition-Sensitive Food Environment Index indicators. It is based on the N-FEI methodology described in: [https://doi.org/10.55845/jos-2025-1116](https://doi.org/10.55845/jos-2025-1116)

## Indicator construction workflow

A typical N-FEI workflow follows these stages:

1. Start with raw vendor, food availability, sanitation, and spatial data.
2. Validate coordinate and required input columns.
3. Compute individual food environment indicators.
4. Use spatial aggregation where indicators require environmental exposure around vendors.
5. Scale indicators to a common range.
6. Invert negative indicators where higher raw values represent poorer food environments.
7. Aggregate selected normalized indicators into a composite score.
8. Compute final NFEI score

## NFEI package architecture and indicator families

### Vendor availability (Availability Module)

Captures **temporal access to food vendors** across the day and week

- Daily availability (weighted by time of day) which captures access across different time periods within a day (morning, afternoon, evening, and night), using a weighted approach that reflects typical consumer purchasing patterns. This is implemented in the package through [`add_daily_availability`](api/availability.md#nfei.availability.add_daily_availability) function
- Weekly availability (days open) which captures access across days of the week, reflecting how consistently vendors operate over time. This is implemented in the package through [`add_weekly_availability`](api/availability.md#nfei.availability.add_weekly_availability) function.
- Overall vendor availability which summarizes temporal access to vendors by taking the row-wise mean of daily availability and weekly availability. This is implemented in the package through [`add_vendor_availability`](api/availability.md#nfei.availability.add_vendor_availability) function.

Reflects real-world accessibility patterns where:
- Morning to evening has higher weight than night
- Full-day and full-week operations imply maximum availability

### Produce color diversity (ProColor Module)

Produce color diversity captures fruit and vegetable availability across six standard color groups, serving as a proxy for **bioactive and micronutrient diversity**.

- Mapping fruits and vegetables into six color groups  
- Counting the presence of these groups at the vendor or environment level.

This complements traditional food group diversity by capturing variation in **micronutrient-rich foods** that may not be fully distinguished by food group classification alone.

This is implemented through:

- [`add_produce_color_diversity`](api/color.md#nfei.color.add_produce_color_diversity) which scans user-specified produce color columns for defined color groups and creates a score representing the number of color groups available for each observation.
- [`count_unique_colors_in_columns`](api/color.md#nfei.color.count_unique_colors_in_columns), a helper function to count the number of distinct produce color groups recorded for each observation across one or more dataframe columns. It is useful when produce color information is spread across multiple columns, such as separate fruit and vegetable color fields.

### Food diversity (Diversity Module)

Food diversity indicators measure the availability of food groups at the vendor level. The food group structure follows the logic of the Minimum Dietary Diversity for Women framework, but is applied to market or vendor-level food availability data rather than individual dietary intake data.

Includes:

- Vendor Healthy Food Diversity Score (MDD-W based)
- Unhealthy food exposure

Key idea:
> Food diversity is a proxy for nutrient adequacy and malnutrition risk.

 In this package, [`add_market_level_diversity_score`](api/diversity.md#nfei.diversity.add_market_level_diversity_score) computes the Market-Level Diversity Score (MLDS), a vendor-level food diversity indicator used in the NFEI workflow. It counts how many of the 10 required food groups are available for each observation.

### Vendor density and distribution (Density Module)

Vendor density indicators relate vendor counts to population and land area, capturing:

- Vendors per population
- Vendors per km²

Used to assess:
- Over-concentration vs under-service
- Accessibility at population level

These are implemented through:

- [`estimate_population_from_radius`](api/density.md#nfei.density.estimate_population_from_radius) which estimates the population covered by a radius-based survey area. It supports NFEI workflows where vendor mapping is conducted using a centred approach, such as mapping all vendors within a fixed radius around a market, neighbourhood centre, or other reference point.
- [`add_vendor_density`](api/density.md#nfei.density.add_vendor_density) which computes vendor density indicators used in the NFEI workflow. It counts vendors by area and vendor type, then relates those counts to population and land area denominators.

### Spatial exposure (Spatial Module)

Some N-FEI indicators require considering what is available around a vendor, not only at the vendor, thereby capturing **environmental exposure**. Spatial relationships are central to food environment analysis because:
> consumers do not interact only with a single vendor. They interact with clusters of food vendors, nearby infrastructure, and the broader set of food options available within walking distance or another meaningful exposure radius.

Spatial aggregation is implemented through:

- [`calc_distance`](api/spatial.md#nfei.spatial.calc_distance), which measures the closest distance between one set of observations and another, such as households to vendors or vendors to water and sanitation facilities.
- [`features_proximity_agg`](api/spatial.md#nfei.spatial.features_proximity_agg), which summarizes the features available within a defined radius around each observation, such as food group diversity within 50 metres or sanitation access within 500 metres.

### Scaling and inversion (Scaling Module)
Different food environment indicators are measured in varying units and scales, such as counts, percentages, or densities, making them not directly comparable in their raw form.

To address this, indicators are linearly scaled to a common range, typically 0 to 10, allowing them to be meaningfully compared and combined into a composite index. Indicators representing less desirable conditions are inverted during scaling so that higher scores consistently reflect healthier food environments.

This is implemented through:

- [`create_linear_scale`](api/scaling.md#nfei.scaling.create_linear_scale), which transforms a numeric column into a standardized score using linear scaling. It can optionally adjust this normalization using an expected maximum value, invert the resulting scores, and then rescale them to a user-defined range.

### Validation
Data validation ensures the reliability of inputs used in N-FEI analysis, particularly for spatial and numeric variables where errors can distort results.

These steps are typically applied early in the workflow to ensure that subsequent spatial, density, and exposure indicators are based on consistent and reliable data.

Spatial and numeric quality checks are supported through:

- [`fix_spatial_outliers`](api/validation.md#nfei.validation.fix_spatial_outliers), which identifies and corrects outliers in geographic coordinate data using the Median Absolute Deviation (MAD) method. It is designed for NFEI workflows where inaccurate latitude and longitude values can distort distance calculations, spatial aggregation, and density estimation.
- [`mad_based_outlier`](api/validation.md#nfei.validation.mad_based_outlier), although a helper function, this function is used within [`fix_spatial_outliers`](api/validation.md#nfei.validation.fix_spatial_outliers) and can be used beyond NFEI framework, to detect extreme values in skewed distributions, particularly for spatial coordinates where traditional mean-based methods are not robust.

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

## Quick links

- [Getting started](getting-started.md): installation, imports, and first examples.
- API reference: 
    - [Availability Module](api/availability.md)
    - [ProColor Module](api/color.md)
    - [Diversity Module](api/density.md)
    - [Density Module](api/density.md)
    - [Spatial Module](api/spatial.md)
    - [Scaling Module](api/scaling.md)
    - [Validation Module](api/validation.md)
- [End-to-end example](examples/nfei_end_to_end_example.ipynb): executable end-to-end workflows.