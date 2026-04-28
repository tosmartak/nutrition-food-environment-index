---
toc_depth: 2
---

# ProColor Diversity

The **``color``** module provides functions for constructing produce color diversity
indicators used in the Nutrition-Sensitive Food Environment Index (NFEI).

In food environment analysis, diversity is not only defined by the number of
food groups available, but also by the variety of fruits and vegetables offered.
Produce color diversity serves as a practical proxy for variation in
micronutrient-rich foods, as different color groups are often associated with
different vitamins, minerals, and bioactive compounds.

This module operationalizes produce diversity by scanning vendor-level data for
predefined color groups and summarizing their presence into a single indicator.
The approach is consistent with the NFEI workflow, where color diversity is used
to complement food group diversity and provide additional insight into the
nutritional quality of the food environment.

The module supports data structures where produce color information is stored as:

- single color values (e.g., ``"Red"``), or  
- comma-separated values (e.g., ``"Red, Yellow_Orange"``), reflecting multiple
  produce types available at a vendor.

Three core functions are provided:

- **`add_produce_color_diversity`**, which constructs the main color diversity
  indicator by identifying the presence of predefined color groups and counting
  how many are available per observation.
- **`count_unique_colors_in_columns`**, which counts the number of distinct color
  values across one or more columns without enforcing predefined color groups.

Together, these functions enable flexible construction of produce color
indicators, supporting both strict NFEI-aligned scoring and custom exploratory
analyses of fruit and vegetable diversity.

::: nfei.color.add_produce_color_diversity
    options:
      heading: Add produce color diversity indicators
      toc_label: Add produce color diversity indicators

::: nfei.color.count_unique_colors_in_columns
    options:
      heading: Count unique produce colors across selected columns
      toc_label: Count unique produce colors across selected columns

<!-- ::: nfei.color.color_exists
    options:
      heading: Color exists in columns
      toc_label: Color exists in columns -->
