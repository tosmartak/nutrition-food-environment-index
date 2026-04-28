from __future__ import annotations

import math
import pandas as pd


def estimate_population_from_radius(
    population: float,
    land_area_sqkm: float,
    radius_km: float,
    round_area: int | None = 2,
    round_population: int | None = 0,
) -> dict[str, float]:
    """
    This function estimates the population covered by a radius-based survey
    area. It supports NFEI workflows where vendor mapping is conducted using a
    centred approach, such as mapping all vendors within a fixed radius around a
    market, neighbourhood centre, or other reference point.

    The function assumes that population is evenly distributed across the larger
    known administrative area. It then estimates the population within the
    circular mapped area using the radius supplied by the user.

    Parameters
    ----------
    population:
        Total population of the larger administrative area used as the
        denominator. For example, this may be the population of a city,
        municipality, arrondissement, ward, or subcounty.

    land_area_sqkm:
        Total land area, in square kilometres, of the same administrative area
        represented by ``population``.

    radius_km:
        Radius, in kilometres, of the mapped survey area.

    round_area:
        Number of decimal places used to round the estimated mapped area. If
        None, no rounding is applied. The default is 2.

    round_population:
        Number of decimal places used to round the estimated population. If
        None, no rounding is applied. The default is 0.

    Returns
    -------
    dict[str, float]
        Dictionary containing:

        - ``"population_density_per_sqkm"``: population divided by land area.
        - ``"area_covered_sqkm"``: estimated circular mapped area.
        - ``"estimated_population"``: estimated population within the mapped
          radius.

    Raises
    ------
    ValueError
        If ``population``, ``land_area_sqkm``, or ``radius_km`` is less than or
        equal to zero.

    Notes
    -----
    The estimated mapped area is calculated as:

    ``pi * radius_km^2``

    The estimated population is calculated as:

    ``(population / land_area_sqkm) * area_covered_sqkm``

    This is an approximation. It should be interpreted as an estimated
    denominator, especially in settings where population is not evenly
    distributed across the administrative area.

    Examples
    --------
    Estimate the population covered by a 1 km radius survey area:

    >>> import nfei
    >>>
    >>> result = nfei.estimate_population_from_radius(
    ...     population=738444,
    ...     land_area_sqkm=79,
    ...     radius_km=1,
    ... )

    Return unrounded estimates:

    >>> result = nfei.estimate_population_from_radius(
    ...     population=738444,
    ...     land_area_sqkm=79,
    ...     radius_km=1,
    ...     round_area=None,
    ...     round_population=None,
    ... )
    """
    
    if population <= 0:
        raise ValueError("population must be greater than zero.")

    if land_area_sqkm <= 0:
        raise ValueError("land_area_sqkm must be greater than zero.")

    if radius_km <= 0:
        raise ValueError("radius_km must be greater than zero.")

    population_density = population / land_area_sqkm
    area_covered = math.pi * (radius_km**2)
    estimated_population = population_density * area_covered

    if round_area is not None:
        area_covered = round(area_covered, round_area)

    if round_population is not None:
        estimated_population = round(estimated_population, round_population)

    return {
        "population_density_per_sqkm": population_density,
        "area_covered_sqkm": area_covered,
        "estimated_population": estimated_population,
    }


def add_vendor_density(
    df: pd.DataFrame,
    group_col: str,
    vendor_type_col: str,
    population_col: str,
    land_area_col: str,
    count_col: str = "vendor_type_pop",
    per_pop_col: str = "vendor_type_per_pop",
    per_sqkm_col: str = "vendor_type_per_sqkm",
    rate_per: float | None = None,
    rate_col: str | None = None,
) -> pd.DataFrame:
    """
    This function computes vendor density indicators used in the NFEI workflow.
    It counts vendors by area and vendor type, then relates those counts to
    population and land area denominators.

    The function produces two core indicators:

    - vendors per population, reflecting vendor availability relative to the
      number of people living in the area.
    - vendors per square kilometre, reflecting the spatial distribution or
      concentration of vendors across the mapped area.

    These indicators help describe whether a food environment may be
    under-served, over-concentrated, or spatially dense relative to the
    population and land area being assessed.

    Parameters
    ----------
    df:
        Input dataframe. Each row should represent a vendor or vendor
        observation.

    group_col:
        Column identifying the geographic unit, mapped area, or administrative
        unit within which vendor counts should be computed. Examples include
        ``"ward"``, ``"subcounty"``, ``"community"``, or ``"survey_area"``.

    vendor_type_col:
        Column identifying the vendor category or vendor type. Vendor counts are
        calculated separately for each combination of ``group_col`` and
        ``vendor_type_col``.

    population_col:
        Column containing the population denominator for each group. This can be
        a known administrative population or an estimated mapped-area population
        from :func:`estimate_population_from_radius`.

    land_area_col:
        Column containing land area in square kilometres for each group. This
        can be a known administrative land area or an estimated mapped-area
        coverage.

    count_col:
        Name of the output column containing the vendor count by group and
        vendor type. The default is ``"vendor_type_pop"``.

    per_pop_col:
        Name of the output column containing vendors per person. The default is
        ``"vendor_type_per_pop"``.

    per_sqkm_col:
        Name of the output column containing vendors per square kilometre. The
        default is ``"vendor_type_per_sqkm"``.

    rate_per:
        Optional population scaling factor used to create an easier-to-read
        rate. For example, ``rate_per=1000`` creates vendors per 1,000 people.
        If None, no scaled rate column is created.

    rate_col:
        Optional name of the scaled population density column. If not provided
        and ``rate_per`` is used, the column name is generated automatically
        from ``per_pop_col`` and ``rate_per``.

    Returns
    -------
    pd.DataFrame
        Copy of the dataframe with vendor count, vendors per population, vendors
        per square kilometre, and optionally a scaled population-rate column
        added.

    Raises
    ------
    KeyError
        If any of ``group_col``, ``vendor_type_col``, ``population_col``, or
        ``land_area_col`` is not found in the dataframe.

    ValueError
        If any value in ``population_col`` or ``land_area_col`` is less than or
        equal to zero, or if ``rate_per`` is provided and is less than or equal
        to zero.

    Notes
    -----
    Vendor counts are calculated for each unique combination of geographic group
    and vendor type. The resulting count is merged back onto the original
    dataframe, so each vendor row receives the count and density values for its
    own group and vendor type.

    The main calculations are:

    ``vendor_type_per_pop = vendor_type_count / population``

    ``vendor_type_per_sqkm = vendor_type_count / land_area_sqkm``

    If ``rate_per`` is provided, the scaled rate is calculated as:

    ``vendor_type_per_pop * rate_per``

    Examples
    --------
    Compute vendor density using known population and land-area denominators:

    >>> import pandas as pd
    >>> import nfei
    >>>
    >>> df = pd.DataFrame(
    ...     {
    ...         "ward": ["A", "A", "A", "B"],
    ...         "vendor_type": ["shop", "shop", "kiosk", "shop"],
    ...         "Population": [1000, 1000, 1000, 800],
    ...         "Land_area_sqkm": [2.0, 2.0, 2.0, 1.5],
    ...     }
    ... )
    >>> result = nfei.add_vendor_density(
    ...     df,
    ...     group_col="ward",
    ...     vendor_type_col="vendor_type",
    ...     population_col="Population",
    ...     land_area_col="Land_area_sqkm",
    ... )

    Add an interpretable scaled rate, such as vendors per 1,000 people:

    >>> result = nfei.add_vendor_density(
    ...     df,
    ...     group_col="ward",
    ...     vendor_type_col="vendor_type",
    ...     population_col="Population",
    ...     land_area_col="Land_area_sqkm",
    ...     rate_per=1000,
    ... )

    Use custom output column names:

    >>> result = nfei.add_vendor_density(
    ...     df,
    ...     group_col="ward",
    ...     vendor_type_col="vendor_type",
    ...     population_col="Population",
    ...     land_area_col="Land_area_sqkm",
    ...     count_col="vendor_count",
    ...     per_pop_col="vendors_per_person",
    ...     per_sqkm_col="vendors_per_sqkm",
    ...     rate_per=1000,
    ...     rate_col="vendors_per_1000_people",
    ... )
    """
    
    required_cols = [group_col, vendor_type_col, population_col, land_area_col]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Missing required column(s): {missing_cols}")

    if (df[population_col] <= 0).any():
        raise ValueError(f"All values in '{population_col}' must be greater than zero.")

    if (df[land_area_col] <= 0).any():
        raise ValueError(f"All values in '{land_area_col}' must be greater than zero.")

    new_df = df.copy()

    vendor_counts = (
        new_df.groupby([group_col, vendor_type_col])
        .size()
        .reset_index(name=count_col)
    )

    new_df = pd.merge(
        new_df,
        vendor_counts,
        on=[group_col, vendor_type_col],
        how="left",
    )

    new_df[per_pop_col] = new_df[count_col] / new_df[population_col]
    new_df[per_sqkm_col] = new_df[count_col] / new_df[land_area_col]

    if rate_per is not None:
        if rate_per <= 0:
            raise ValueError("rate_per must be greater than zero.")

        if rate_col is None:
            clean_rate = int(rate_per) if float(rate_per).is_integer() else rate_per
            rate_col = f"{per_pop_col}_per_{clean_rate}"

        new_df[rate_col] = new_df[per_pop_col] * rate_per

    return new_df