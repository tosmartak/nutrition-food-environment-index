# 📦 NFEI – Nutrition-Sensitive Food Environment Index (Python Package) Documentation

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Package](https://img.shields.io/badge/package-nfei-brightgreen)
![Status](https://img.shields.io/badge/status-active%20development-orange)
![Research](https://img.shields.io/badge/research--backed-N--FEI-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

`nfei` is a Python package for computing nutrition-sensitive food environment indicators from vendor survey data, food availability data, and geospatial data. It provides reusable functions for building the indicator components used in the Nutrition-Sensitive Food Environment Index (N-FEI), including food diversity, produce color diversity, vendor availability, vendor density, spatial aggregation, scaling, and validation.

This package is designed for researchers, data scientists, public-health analysts, food-system practitioners, and policy teams who want to move from raw food environment data to transparent, reproducible indicators.

## What is N-FEI?
The **Nutrition-Sensitive Food Environment Index (N-FEI)** is a composite food environment assessment framework developed to evaluate how the built food environment may support or constrain healthier diets and public-health outcomes. It is designed to assess food environments through a **nutrition and public health lens**, capturing how food availability, accessibility, infrastructure, and exposure to unhealthy foods interact to influence malnutrition risk.

The N-FEI methodology was developed and validated using multi-country food environment data. The published paper describes the conceptual basis, indicator selection, spatial logic, sensitivity analysis, validation strategy, and policy relevance of the index.

**Methodology paper:** [https://doi.org/10.55845/jos-2025-1116](https://doi.org/10.55845/jos-2025-1116)

It is grounded in the definition of food environments as:

> “the collective physical, economic, policy, and sociocultural surroundings, opportunities, and conditions that influence people’s food and beverage choices and nutritional status.”

The N-FEI expands food environment measurement beyond affordability alone. The index is constructed from **nine indicators**, normalized and aggregated into a **0–10 scale**, where higher values indicate healthier food environments. It focuses on observable features of vendor environments, including:

1. **Vendor Healthy Food Diversity Score**, using food groups aligned with the Minimum Dietary Diversity for Women framework.
2. **Vendor Environment Healthy Food Diversity Score**, capturing what is available around vendors, not only at a single vendor.
3. **Vendor ProColor Diversity Score**, Fruit and vegetable color diversity reflecting ProColor-style produce diversity.
4. **Vendor Environment ProColor Diversity Score**, capturing the broader produce-color environment around vendors.
5. **Access to Water and Sanitation**, especially relevant for informal and mobile food vendors.
6. **Vendor availability**, measured through daily and weekly operating patterns.
7. **Vendor density per population**, capturing vendor availability relative to population size.
8. **Vendor density per square kilometre**, capturing geographic distribution.
9. **Unhealthy food count**, capturing exposure to selected unhealthy beverages and snacks.

This package does **not** hide the index inside a black-box function. Instead, it exposes the building blocks used to compute the indicators, so users can adapt the workflow to their own study design, data structure, and policy context.

## What this package does

`nfei` helps you:

- Compute vendor-level food diversity indicators.
- Compute produce color diversity indicators.
- Compute unhealthy beverage, snack, and total unhealthy food counts.
- Compute daily, weekly, and combined vendor availability.
- Estimate population covered by radius-based vendor mapping.
- Compute vendor density by population and land area.
- Aggregate food environment features within spatial buffers.
- Calculate nearest distances and spatial aggregations for enviromental exposure around a point.
- Scale indicators to a common interpretation range.
- Detect and correct coordinate outliers using a robust MAD-based approach.

The package is especially useful when your raw survey data contains binary food availability columns, comma-separated produce color fields, vendor operating days or hours, latitude and longitude, vendor type, population denominators, and land-area denominators.

## Citation

If you use this package or the N-FEI methodology, please cite:

```text
Akingbemisilu, T. H., Jordan, I., Asiimwe, R., Bodjrenou, S., Nabuuma, D., Odongo, N., Onyango, K. O., Teferi, E., Tokeshi, C., Lundy, M., & Termote, C. (2025). The Nutrition-Sensitive Food Environment Index: A Comprehensive Approach to Assessing Food Environments in Association with Health Risks for Policy Decision Making. Journal of Sustainability, 1(1). https://doi.org/10.55845/jos-2025-1116
```

DOI: [https://doi.org/10.55845/jos-2025-1116](https://doi.org/10.55845/jos-2025-1116)

## Quick links

- [Methodology](methodology.md): how the package maps to the N-FEI indicator workflow.
- [Getting started](getting-started.md): installation, imports, and first examples.
- [End-to-end example](examples/nfei_end_to_end_example.ipynb): executable end-to-end workflows.
- [API reference: Availability](api/availability.md): automatically generated function documentation from docstrings.