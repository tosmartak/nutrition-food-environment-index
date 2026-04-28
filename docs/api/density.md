---
toc_depth: 2
---

# Density

The **``density``** module provides functions for constructing vendor density and distribution indicators used in the Nutrition-Sensitive Food Environment Index (NFEI).

In food environment analysis, vendor presence is not only about the total number of vendors observed. It also matters how vendor counts relate to the population served and the size of the mapped area. A location with many vendors may still be underserved if the population is large, while a smaller location may appear well supplied if vendor availability is high relative to its population or land area.

This module supports two related measurement needs:

- **Population-based vendor density**, which relates vendor counts to the
  population denominator of the mapped area.
- **Area-based vendor distribution**, which relates vendor counts to land area
  in square kilometres.

The module also includes a helper function for estimating the population covered by a circular mapped area. This is particularly useful for centred food environment surveys, where vendors are mapped within a fixed radius but the population denominator must be estimated from a larger administrative area.

Together, these functions help users construct interpretable density and
distribution indicators that complement food diversity, availability, and
spatial exposure measures within the NFEI framework.

::: nfei.density.estimate_population_from_radius
    options:
      heading: Estimate population coverage for a circular mapped area
      toc_label: Estimate population coverage for a circular mapped area

::: nfei.density.add_vendor_density
    options:
      heading: Add vendor density and distribution indicators
      toc_label: Add vendor density and distribution indicators