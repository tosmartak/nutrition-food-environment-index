# 📦 NFEI – Nutrition-Sensitive Food Environment Index (Python Package)

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/tosmartak/nutrition-food-environment-index/actions/workflows/ci.yml/badge.svg)
![Docs](https://github.com/tosmartak/nutrition-food-environment-index/actions/workflows/docs.yml/badge.svg)
![Status](https://img.shields.io/badge/status-active%20development-orange)
![Research](https://img.shields.io/badge/research--backed-N--FEI-purple)
<!-- ![PyPI](https://img.shields.io/pypi/v/nfei) -->

`nfei` is a Python package for computing nutrition-sensitive food environment indicators from vendor survey data, food availability data, and geospatial data. It provides reusable functions for building the indicator components used in the Nutrition-Sensitive Food Environment Index (N-FEI), including food diversity, produce color diversity, vendor availability, vendor density, spatial aggregation, scaling, and validation.

This package is designed for researchers, data scientists, public-health analysts, food-system practitioners, and policy teams who want to move from raw food environment data to transparent, reproducible indicators.

## 🧠 What is the Nutrition-Sensitive Food Environment Index?

The **Nutrition-Sensitive Food Environment Index (N-FEI)** is a composite food environment assessment framework developed to evaluate how the built food environment may support or constrain healthier diets and public-health outcomes. It is designed to assess food environments through a **nutrition and public health lens**, capturing how food availability, accessibility, infrastructure, and exposure to unhealthy foods interact to influence malnutrition risk.

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

The N-FEI methodology was developed and validated using multi-country food environment data. The published paper describes the conceptual basis, indicator selection, spatial logic, sensitivity analysis, validation strategy, and policy relevance of the index.

**Methodology paper:**  
https://doi.org/10.55845/jos-2025-1116

This package does **not** hide the index inside a black-box function. Instead, it exposes the building blocks used to compute the indicators, so users can adapt the workflow to their own study design, data structure, and policy context.

## 🎯 What this package does

`nfei` helps you:

- Compute vendor-level food diversity indicators.
- Compute produce color diversity indicators.
- Compute unhealthy beverage, snack, and total unhealthy food counts.
- Compute daily, weekly, and combined vendor availability.
- Estimate population covered by radius-based vendor mapping.
- Compute vendor density by population and land area.
- Aggregate food environment features within spatial buffers.
- Calculate nearest distances and spatial aggregations for enviromental exposure.
- Scale indicators to a common interpretation range.
- Detect and correct coordinate outliers using a robust MAD-based approach.

The package is especially useful when your raw survey data contains binary food availability columns, comma-separated produce color fields, vendor operating days or hours, latitude and longitude, vendor type, population denominators, and land-area denominators.

## ⚙️ Installation

From PyPI, once released:

```bash
pip install nfei
```

For local development from the repository root:

```bash
pip install -e .
```

To run tests:

```bash
pytest
```

## 🧱 NFEI package architecture

### 1. Availability Module
Captures **temporal access to food vendors**

- Daily availability (weighted by time of day)
- Weekly availability (days open)

Reflects real-world accessibility patterns where:
- Morning to evening has higher weight than night
- Full-day and full-week operations imply maximum availability


### 2. Diversity Module
Captures **nutritional quality of the food environment**

Includes:

- Vendor Healthy Food Diversity Score (MDD-W based)
- Environment-level diversity (spatial aggregation)
- Unhealthy food exposure

Key idea:
> Food diversity is a proxy for nutrient adequacy and malnutrition risk.


### 3. Color Diversity Module
Captures **bioactive nutrient diversity** using ProColor

- Maps fruits and vegetables into 6 color groups
- Counts presence across vendors or environments

This complements traditional food group diversity by capturing **micronutrient richness**


### 4. Density Module
Captures **market structure and saturation**

- Vendors per population
- Vendors per km²

Used to assess:
- Over-concentration vs under-service
- Accessibility at population level


### 5. Spatial Module
Captures **environmental exposure**

- Distance calculations
- Buffer-based aggregation (e.g., 50m radius)

This is critical because:
> Consumers interact with food environments, not just individual vendors


### 6. Scaling Module
Handles **normalization and comparability**

- Aligns indicators to common scale (0–10)
- Supports inversion (e.g., unhealthy food)


### 7. Validation Module
Ensures **data quality and robustness**

- Outlier detection
- Spatial consistency checks

---

## N-FEI specific indicator construction logic

An N-FEI style indicator construction workflow usually involves these steps:

1. Start with raw vendor, food availability, sanitation, and spatial data.
2. Validate coordinate and required input columns.
3. Compute individual food environment indicators.
4. Use spatial aggregation where indicators require environmental exposure around vendors.
5. Scale indicators to a common range.
6. Invert negative indicators where higher raw values represent poorer food environments.
7. Aggregate selected normalized indicators into a composite score.
8. Compute final NFEI score

### Step 1: Compute raw indicators

Examples:

- `mlds`
- `overall_color`
- `perc_vendor_avail`
- `vendor_type_per_pop`
- `vendor_type_per_sqkm`
- `unhealthy_food_count`

### Step 2: Add spatial exposure indicators when needed

Examples:

- food diversity within 50 metres
- produce color diversity within 50 metres
- sanitation or water access within 500 metres

### Step 3: Normalize indicators to a common scale

Use `create_linear_scale` to align indicators to a common 0–10 interpretation.

### Step 4: Invert negative indicators

Unhealthy food exposure should usually be inverted before aggregation.

### Step 5: Aggregate selected normalized indicators

The published N-FEI uses a simple unweighted aggregation of normalized indicators. In practice, users should only aggregate indicators that are available and appropriate for their dataset.

Example:

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

---

## Complete example notebook

A fully reproducible simulated end-to-end workflow is provided [in the end-to-end online documentation](https://tosmartak.github.io/nutrition-food-environment-index/examples/nfei_end_to_end_example/)

The notebook demonstrates with the use of a simulated data:

- computing MLDS
- computing produce color diversity
- computing daily and weekly availability
- computing unhealthy food count
- computing vendor density
- computing spatial proximity aggregation
- scaling indicators
- assembling a simple N-FEI-style composite score

The example is intentionally simulated so users can run it without access to restricted or project-specific survey data.

---

## Important notes and data assumptions

1. This package provides indicator-building functions, not a single one-size-fits-all N-FEI button.
2. Column names are never assumed. Users must map their own dataset columns.
3. Binary variables are coded as 0/1
4. Multi-response fields are comma-separated strings or already coverted to binary columns
5. Spatial coordinates are in decimal degrees
6. Missing values are handled explicitly where relevant.
7. Spatial functions assume latitude and longitude are in decimal degrees unless otherwise specified.
8. The final composite index should be assembled using indicators that are valid for the user’s specific study design.

---

## Repository structure

Suggested project structure:

```text
nutrition-food-environment-index/
├── docs/
│   └── api/
│       ├── availability.md
│       ├── color.md
│       ├── density.md
│       ├── diversity.md
│       ├── scaling.md
│       ├── spatial.md
│       └── validation.md
│   ├── examples/
│       └── nfei_end_to_end_example.ipynb
│   ├── getting-started.md
│   ├── methodology.md
│   └── index.md
├── src/
│   └── nfei/
│       ├── availability.py
│       ├── color.py
│       ├── density.py
│       ├── diversity.py
│       ├── scaling.py
│       ├── spatial.py
│       ├── validation.py
│       └── __init__.py
├── tests/
│   ├── test_availability.py
│   ├── test_color.py
│   ├── test_density.py
│   ├── test_diversity.py
│   ├── test_public.py
│   ├── test_scaling.py
│   ├── test_spatial.py
│   └── test_validation.py
├── README.md
├── CITATION.cff
├── LICENSE
├── mkdocs.yml
└── pyproject.toml
```

---

## Citation

If you use this package or the N-FEI methodology, please cite:

> Akingbemisilu, T. H., Jordan, I., Asiimwe, R., Bodjrenou, S., Nabuuma, D., Odongo, N., Onyango, K. O., Teferi, E., Tokeshi, C., Lundy, M., & Termote, C. (2025). The Nutrition-Sensitive Food Environment Index: A Comprehensive Approach to Assessing Food Environments in Association with Health Risks for Policy Decision Making. *Journal of Sustainability*, *1*(1). [https://doi.org/10.55845/jos-2025-1116](https://doi.org/10.55845/jos-2025-1116)

---

## Contributing

Contributions are welcome. Please ensure that new functionality:

- follows the transparent, modular design of the package
- includes tests
- avoids hidden assumptions about user column names
- documents expected input format and output interpretation
- remains aligned with food environment measurement logic

---

## License

MIT License.

