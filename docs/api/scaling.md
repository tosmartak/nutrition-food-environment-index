---
toc_depth: 2
---

# Scaling

The scaling module provides functions for transforming raw indicator values
into standardized scores used in the Nutrition-Sensitive Food Environment Index
(NFEI).

In food environment analysis, different indicators are measured in different
units and ranges. For example, vendor density may be expressed as counts per
population, while availability is measured as a percentage, and diversity is
measured as a count of food groups. These indicators are not directly comparable
in their raw form.

This module addresses this challenge by applying linear scaling to convert
indicators into a common interpretation range, typically from 0 to 10. This
ensures that multiple indicators can be meaningfully compared and combined into
a composite index.

The module also supports inversion of indicators where higher raw values
represent less desirable conditions. For example, unhealthy food counts can be
inverted so that higher scaled scores consistently represent healthier food
environments.

The scaling approach used in this module mirrors the NFEI workflow, ensuring that
final indicator scores are interpretable, comparable, and suitable for
aggregation into composite measures.

::: nfei.scaling.create_linear_scale
    options:
      heading: Linear scaling
      toc_label: Linear scaling