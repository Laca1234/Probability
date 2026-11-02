"""Typed concepts used by the probability engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Literal

EvidenceStatus = Literal["observed", "derived", "assumed", "unknown", "illustrative"]
DatasetKind = Literal["original", "derived", "estimated", "synthetic", "unknown"]


class ModelInputError(ValueError):
    """Raised when a model input is outside its documented domain."""


class DoubleCountingError(ModelInputError):
    """Raised when the same event is multiplied into a probability chain twice."""


@dataclass(frozen=True, slots=True)
class BirthRecord:
    country_code: str
    country_name: str
    continent: str
    year: int
    births: int

    def __post_init__(self) -> None:
        if len(self.country_code) != 3 or not self.country_code.isascii() or not self.country_code.isalpha():
            raise ModelInputError(f"Invalid ISO 3166-1 alpha-3 code: {self.country_code!r}")
        if self.country_code != self.country_code.upper():
            raise ModelInputError("Country codes must be uppercase.")
        if not 1 <= self.year <= 9999:
            raise ModelInputError("Year must be between 1 and 9999.")
        if isinstance(self.births, bool) or not isinstance(self.births, int) or self.births < 0:
            raise ModelInputError("Birth counts must be non-negative integers.")
        if not self.country_name.strip() or not self.continent.strip():
            raise ModelInputError("Country name and continent are required.")


@dataclass(frozen=True, slots=True)
class DatasetProvenance:
    dataset_id: str
    name: str
    publisher: str
    source_url: str
    accessed_on: str
    reference_period: str
    license: str
    version: str
    sha256: str
    kind: DatasetKind
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BirthDataset:
    records: tuple[BirthRecord, ...]
    provenance: DatasetProvenance

    def __post_init__(self) -> None:
        if not self.records:
            raise ModelInputError("A birth dataset must contain at least one record.")
        seen: set[tuple[str, int]] = set()
        rows_by_country: dict[str, int] = {}
        years: set[int] = set()
        for row in self.records:
            key = (row.country_code, row.year)
            if key in seen:
                raise ModelInputError(f"Duplicate country-year record: {row.country_code} {row.year}.")
            seen.add(key)
            rows_by_country[row.country_code] = rows_by_country.get(row.country_code, 0) + 1
            years.add(row.year)
        incomplete = [code for code, row_count in rows_by_country.items() if row_count != len(years)]
        if incomplete:
            raise ModelInputError(
                "Dataset must contain every selected country-year cell; use an explicit zero only "
                "when the source confirms a zero count. Incomplete series: " + ", ".join(sorted(incomplete)[:10])
            )

    @property
    def years(self) -> tuple[int, ...]:
        return tuple(sorted({row.year for row in self.records}))

    @property
    def countries(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted({(row.country_code, row.country_name) for row in self.records}, key=lambda x: x[1]))


@dataclass(frozen=True, slots=True)
class ProbabilityFactor:
    """One conditional factor in a chain-rule decomposition.

    ``event_id`` names the newly added event. ``conditioned_on`` lists event IDs
    already established by earlier factors. Multiplying a repeated event is rejected.
    """

    event_id: str
    label: str
    probability: Fraction | None
    denominator: str
    formula: str
    evidence: EvidenceStatus
    source: str
    conditioned_on: tuple[str, ...] = ()
    assumption_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ModelInputError("Every probability factor needs an event identifier.")
        if self.probability is not None and not 0 <= self.probability <= 1:
            raise ModelInputError(f"Factor {self.event_id!r} must be in [0, 1].")


@dataclass(frozen=True, slots=True)
class ProbabilityChain:
    factors: tuple[ProbabilityFactor, ...]
    value: Fraction | None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    country_code: str
    start_year: int
    end_year: int
    max_birth_year_gap: int
    meeting_probability: Fraction | None = None
    relationship_probability: Fraction | None = None
    meeting_channel: str = "Unknown / not specified"
    notes: str = ""
    dataset_id: str = ""

    def __post_init__(self) -> None:
        if self.start_year > self.end_year:
            raise ModelInputError("Start year must not be after end year.")
        if self.max_birth_year_gap < 0:
            raise ModelInputError("Age or birth-year gap must be non-negative.")
        if len(self.country_code) != 3 or not self.country_code.isalpha() or not self.country_code.isupper():
            raise ModelInputError("Select a valid uppercase ISO alpha-3 country code.")
        for key, p in (("meeting", self.meeting_probability), ("relationship", self.relationship_probability)):
            if p is not None and not 0 <= p <= 1:
                raise ModelInputError(f"{key.title()} probability must be between 0 and 1.")


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario: Scenario
    chain: ProbabilityChain
    population_size: int
    target_country_births: int
    eligible_country_pairs: int
    all_population_pairs: int
    demographic_probability: Fraction
    result_scope: str = "Two distinct people sampled without replacement from births in the selected cohort"
    metadata: dict[str, object] = field(default_factory=dict)

