---
toc_depth: 2
---

# Diversity

The diversity module provides functions for constructing food availability and
food diversity indicators used in the Nutrition-Sensitive Food Environment Index (NFEI).

In food environment analysis, diversity is a central dimension of nutritional
quality. A food environment that offers a wider range of food groups is more
likely to support adequate and balanced diets, while limited diversity may
constrain dietary choices and increase the risk of nutrient deficiencies.

This module operationalizes diversity through two complementary approaches:

- **Healthy food diversity**, measured using the Market-Level Diversity Score
  (MLDS), which counts the availability of key food groups aligned with the
  Minimum Dietary Diversity for Women framework.
- **Unhealthy food exposure**, measured by counting the availability of selected unhealthy beverages and snacks, providing a counterpoint to healthy food diversity within the same environment.

These indicators are designed to work with vendor- or market-level survey data where food availability is recorded as binary or numeric variables across multiple food items.

The module also includes a general-purpose utility function for counting item
availability across selected columns. This supports flexible construction of
custom indicators beyond the predefined NFEI measures.

Together, these functions enable users to construct interpretable food
availability indicators that capture both the presence of diverse, nutrient-rich foods and the exposure to less healthy options, forming a key component of the NFEI framework.

::: nfei.diversity.add_market_level_diversity_score
    options:
      heading: Add Market-Level Diversity Score (MLDS)
      toc_label: Add Market-Level Diversity Score (MLDS)

::: nfei.diversity.add_unhealthy_food_count
    options:
      heading: Create unhealthy beverage, snack, and total unhealthy food counts
      toc_label: Create unhealthy beverage, snack, and total unhealthy food counts

::: nfei.diversity.count_available_items
    options:
      heading: Count available items across selected columns
      toc_label: Count available items across selected columns