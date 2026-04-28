---
toc_depth: 2
---

# Validation

The validation module provides functions for detecting and correcting data
quality issues in the Nutrition-Sensitive Food Environment Index (NFEI)
workflow.

Accurate data is critical for food environment analysis. Errors in numeric
values, especially spatial coordinates, can significantly distort distance
calculations, spatial aggregation, and density estimation. Even a small number
of incorrect coordinates can lead to misleading conclusions about access and
exposure.

This module focuses on robust detection and correction of outliers using the
Median Absolute Deviation (MAD) method, which is well suited for skewed and
real-world datasets.

The module supports two key tasks:

- **Outlier detection**, using a robust statistical approach that identifies
  extreme values without being influenced by them.
- **Spatial data correction**, where erroneous latitude and longitude values
  are detected and replaced using representative central values.

These functions are typically applied early in the NFEI workflow to ensure that
subsequent spatial and density analyses are based on reliable and consistent
data.

::: nfei.validation.fix_spatial_outliers
    options:
      heading: Spatial outlier correction
      toc_label: Spatial outlier correction

::: nfei.validation.mad_based_outlier
    options:
      heading: MAD-based outlier detection
      toc_label: MAD-based outlier detection