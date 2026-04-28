---
toc_depth: 2
---

# Availability

The availability module provides functions for constructing vendor availability indicators used in the Nutrition-Sensitive Food Environment Index (N-FEI).

In food environment analysis, availability is not only defined by whether a vendor exists, but also by how consistently that vendor is accessible to consumers throughout the day and across the week. Vendors that operate only during limited hours or on selected days may contribute less to effective food access than vendors that are continuously available.

This module operationalizes availability using two complementary dimensions:

- **Daily availability**, which captures access across different time periods within a day (morning, afternoon, evening, and night), using a weighted approach that reflects typical consumer purchasing patterns.
- **Weekly availability**, which captures access across days of the week, reflecting how consistently vendors operate over time.

These two components can be combined into a single **overall vendor availability indicator**, providing a more complete representation of temporal access to food vendors.

The functions in this module are designed to work with survey-based data where availability is recorded as binary indicators across time periods or days. They also explicitly account for survey designs where “all day” or “all week” responses replace detailed time or day-level inputs.

::: nfei.availability.add_daily_availability
    options:
      heading: Daily availability
      toc_label: Daily availability

::: nfei.availability.add_weekly_availability
    options:
      heading: Weekly availability
      toc_label: Weekly availability

::: nfei.availability.add_vendor_availability
    options:
      heading: Overall vendor availability
      toc_label: Overall vendor availability