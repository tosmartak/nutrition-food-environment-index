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
    Estimate the population covered by a circular mapped area.

    This mirrors the logic used in the original NFEI notebooks where the mapped
    survey area is approximated using a circular radius.

    The function assumes population is evenly distributed across the larger
    administrative area. This is only an approximation and should be reported
    as an estimated denominator.

    Parameters
    ----------
    population:
        Total population of the larger known administrative area.
        Example: total population of Cotonou.

    land_area_sqkm:
        Total land area, in square kilometers, of the same administrative area
        used for the population value.
        Example: total land area of Cotonou.

    radius_km:
        Radius, in kilometers, of the mapped survey area.
        Example: 1 for a 1 km radius survey area.

    round_area:
        Number of decimal places for the estimated mapped area. If None, no
        rounding is applied.

    round_population:
        Number of decimal places for the estimated population. If None, no
        rounding is applied.

    Returns
    -------
    dict
        Dictionary containing:
        - population_density_per_sqkm
        - area_covered_sqkm
        - estimated_population

    Notes
    -----
    estimated_population =
        (population / land_area_sqkm) * (pi * radius_km^2)
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
    Add vendor density indicators to a dataframe.

    This mirrors the original notebook logic:

    vendor_type_pop =
        count of vendors by area/group and vendor type

    vendor_type_per_pop =
        vendor_type_pop / Population

    vendor_type_per_sqkm =
        vendor_type_pop / Land_area_sqkm

    Parameters
    ----------
    df:
        Input dataframe.

    group_col:
        Column identifying the mapped area or administrative unit.
        Examples: 'ward', 'subcounty'.

    vendor_type_col:
        Column identifying vendor category/type.
        Example: 'vendor_type'.

    population_col:
        Column containing population denominator for each group.
        This can be a known administrative population or an estimated mapped-area
        population.

    land_area_col:
        Column containing land area in square kilometers.
        This can be known administrative area or estimated mapped-area coverage.

    count_col:
        Name of the output column for vendor counts by group and vendor type.

    per_pop_col:
        Name of the output column for vendors per person.

    per_sqkm_col:
        Name of the output column for vendors per square kilometer.

    rate_per:
        Optional population scaling factor. If None, no scaled rate is created.
        Example: rate_per=1000 creates vendors per 1,000 people.

    rate_col:
        Optional name of the scaled population density column. If not provided
        and rate_per is used, a default name is generated.

    Returns
    -------
    pd.DataFrame
        Copy of dataframe with vendor count and density columns added.
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