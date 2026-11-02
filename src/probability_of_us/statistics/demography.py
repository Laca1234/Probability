"""Weighted demographic calculations and great-circle distance."""

from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction

from probability_of_us.domain.models import BirthDataset, ModelInputError


def selected_rows(dataset: BirthDataset, start_year: int, end_year: int):
    if start_year > end_year:
        raise ModelInputError("Start year must not exceed end year.")
    return tuple(row for row in dataset.records if start_year <= row.year <= end_year)


def year_counts(dataset: BirthDataset, start_year: int, end_year: int, country_code: str | None = None) -> dict[int, int]:
    result: dict[int, int] = {}
    for row in selected_rows(dataset, start_year, end_year):
        if country_code is None or row.country_code == country_code:
            result[row.year] = result.get(row.year, 0) + row.births
    return dict(sorted(result.items()))


def country_birth_share(dataset: BirthDataset, country_code: str, start_year: int, end_year: int) -> Fraction:
    rows = selected_rows(dataset, start_year, end_year)
    total = sum(row.births for row in rows)
    country = sum(row.births for row in rows if row.country_code == country_code)
    if total <= 0:
        raise ModelInputError("The selected period has no covered births.")
    return Fraction(country, total)


def joint_country_probability(
    country_births_1: int,
    population_1: int,
    country_births_2: int,
    population_2: int,
    *,
    same_population_without_replacement: bool = False,
) -> Fraction:
    """P(both selected people have a birthplace) for one or two sampling populations."""
    for name, n, total in (("person 1", country_births_1, population_1), ("person 2", country_births_2, population_2)):
        if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in (n, total)) or n > total:
            raise ModelInputError(f"Invalid counts for {name}.")
    if population_1 == 0 or population_2 == 0:
        raise ModelInputError("Sampling populations must be non-empty.")
    if same_population_without_replacement:
        if population_1 != population_2 or country_births_1 != country_births_2:
            raise ModelInputError("Without-replacement sampling needs identical population counts.")
        if population_1 < 2:
            raise ModelInputError("At least two people are required for sampling without replacement.")
        return Fraction(country_births_1 * (country_births_1 - 1), population_1 * (population_1 - 1))
    return Fraction(country_births_1, population_1) * Fraction(country_births_2, population_2)


def age_compatibility_probability(
    births_1: Mapping[int, int],
    births_2: Mapping[int, int],
    max_year_gap: int,
    *,
    same_population_without_replacement: bool = False,
) -> Fraction:
    """P(|birth year 1 - birth year 2| <= max gap) for weighted samples."""
    if isinstance(max_year_gap, bool) or not isinstance(max_year_gap, int) or max_year_gap < 0:
        raise ModelInputError("Maximum birth-year gap must be a non-negative integer.")
    if any(count < 0 for count in (*births_1.values(), *births_2.values())):
        raise ModelInputError("Birth-year weights must be non-negative.")
    total_1, total_2 = sum(births_1.values()), sum(births_2.values())
    if total_1 <= 0 or total_2 <= 0:
        raise ModelInputError("Both year distributions must have positive mass.")
    favorable = sum(
        count_1 * count_2
        for year_1, count_1 in births_1.items()
        for year_2, count_2 in births_2.items()
        if abs(year_1 - year_2) <= max_year_gap
    )
    if same_population_without_replacement:
        if dict(births_1) != dict(births_2) or total_1 != total_2:
            raise ModelInputError("Without-replacement age sampling needs identical year distributions.")
        if total_1 < 2:
            raise ModelInputError("At least two people are required for sampling without replacement.")
        favorable -= total_1  # exclude each person's pairing with themself
        denominator = total_1 * (total_1 - 1)
    else:
        denominator = total_1 * total_2
    return Fraction(favorable, denominator)


def age_eligible_pair_count(births_by_year: Mapping[int, int], max_year_gap: int) -> int:
    """Count unique eligible pairs, excluding self-pairs, from year-stratified counts."""
    if max_year_gap < 0:
        raise ModelInputError("Maximum birth-year gap must be non-negative.")
    years = sorted(births_by_year)
    if any(count < 0 for count in births_by_year.values()):
        raise ModelInputError("Birth-year counts must be non-negative.")
    return sum(
        (births_by_year[y] * (births_by_year[y] - 1) // 2 if y == z else births_by_year[y] * births_by_year[z])
        for i, y in enumerate(years)
        for z in years[i:]
        if z - y <= max_year_gap
    )


def country_within_continent_share(dataset: BirthDataset, country_code: str, start_year: int, end_year: int) -> Fraction:
    rows = selected_rows(dataset, start_year, end_year)
    country_rows = [row for row in rows if row.country_code == country_code]
    if not country_rows:
        raise ModelInputError(f"No records found for country {country_code} in the selected period.")
    continents = {row.continent for row in country_rows}
    if len(continents) != 1:
        raise ModelInputError("Country has inconsistent continent classifications across selected years.")
    continent = next(iter(continents))
    continent_total = sum(row.births for row in rows if row.continent == continent)
    country_total = sum(row.births for row in country_rows)
    if continent_total <= 0:
        raise ModelInputError("Continent has no births in selected period.")
    return Fraction(country_total, continent_total)


def continent_birth_share(dataset: BirthDataset, continent: str, start_year: int, end_year: int) -> Fraction:
    rows = selected_rows(dataset, start_year, end_year)
    total = sum(row.births for row in rows)
    continent_total = sum(row.births for row in rows if row.continent == continent)
    if total <= 0:
        raise ModelInputError("The selected period has no covered births.")
    return Fraction(continent_total, total)


def hierarchical_country_share(dataset: BirthDataset, country_code: str, start_year: int, end_year: int) -> Fraction:
    row = next((r for r in dataset.records if r.country_code == country_code), None)
    if row is None:
        raise ModelInputError(f"Unknown country code {country_code}.")
    return continent_birth_share(dataset, row.continent, start_year, end_year) * country_within_continent_share(
        dataset, country_code, start_year, end_year
    )


def haversine_km(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float) -> float:
    for latitude, longitude in ((latitude_1, longitude_1), (latitude_2, longitude_2)):
        if not math.isfinite(latitude) or not math.isfinite(longitude) or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ModelInputError("Coordinates must be finite latitude/longitude values in valid ranges.")
    radians = math.radians
    lat1, lon1, lat2, lon2 = map(radians, (latitude_1, longitude_1, latitude_2, longitude_2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(hav)))

