---
toc_depth: 2
---

# Spatial

The spatial module provides functions for distance calculation and buffer-based
spatial aggregation used in the Nutrition-Sensitive Food Environment Index
(NFEI).

Spatial relationships are central to food environment analysis because consumers
do not interact only with a single vendor. They interact with clusters of food
vendors, nearby infrastructure, and the broader set of food options available
within walking distance or another meaningful exposure radius.

This module supports two main spatial tasks:

- **Nearest-distance calculation**, which measures the closest distance between
  one set of observations and another, such as households to vendors or vendors
  to water and sanitation facilities.
- **Buffer-based feature aggregation**, which summarizes the features available
  within a defined radius around each observation, such as food group diversity
  within 50 metres or sanitation access within 500 metres.

The module is designed to accept ordinary pandas DataFrames with longitude and
latitude columns. For Buffer-based feature aggregation, coordinates are projected
internally before spatial operations are performed, so users can work with
decimal-degree input data while still using metre-based buffers.

These functions help users construct environment-level exposure indicators that
complement vendor-level food diversity, availability, density, and infrastructure
measures in the NFEI workflow.

::: nfei.spatial.calc_distance
    options:
      heading: Nearest distance
      toc_label: Nearest distance

::: nfei.spatial.features_proximity_agg
    options:
      heading: Buffer-based feature aggregation
      toc_label: Buffer-based feature aggregation

::: nfei.spatial.haversine_vectorized
    options:
      heading: Haversine distance
      toc_label: Haversine distance