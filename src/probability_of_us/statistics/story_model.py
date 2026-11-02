"""The main demographic factorization; independent of Qt and persistence."""

from __future__ import annotations

from fractions import Fraction
from probability_of_us.domain.models import EvidenceStatus

from probability_of_us.domain.models import (
    BirthDataset, ProbabilityFactor, Scenario, ScenarioResult, ModelInputError,
)
from probability_of_us.statistics.demography import (
    age_compatibility_probability, age_eligible_pair_count, selected_rows, year_counts,
)
from probability_of_us.statistics.probability import multiply_factors


def analyze_story(dataset: BirthDataset, scenario: Scenario) -> ScenarioResult:
    """Calculate a pair's demographic event, then retain unknown human factors as unknown.

    Sampling frame: two distinct unordered individuals selected without replacement
    from all birth records represented by the dataset within the selected years.
    The same-country and compatible-birth-year event is calculated exactly from counts.
    Encounter and relationship probabilities are user assumptions when supplied.
    """
    if not any(code == scenario.country_code for code, _ in dataset.countries):
        raise ModelInputError(f"No birth records found for {scenario.country_code}.")
    if not selected_rows(dataset, scenario.start_year, scenario.end_year):
        raise ModelInputError("The selected period has no rows in this dataset.")
    world_by_year = year_counts(dataset, scenario.start_year, scenario.end_year)
    country_by_year = year_counts(dataset, scenario.start_year, scenario.end_year, scenario.country_code)
    world_total, country_total = sum(world_by_year.values()), sum(country_by_year.values())
    if world_total < 2:
        raise ModelInputError("At least two people must be represented by the selected population.")
    both_country = Fraction(country_total * (country_total - 1), world_total * (world_total - 1))
    if country_total >= 2:
        age_given_country = age_compatibility_probability(
            country_by_year, country_by_year, scenario.max_birth_year_gap,
            same_population_without_replacement=True,
        )
    else:
        # The preceding event has probability zero; this zero conditional factor is
        # explicit and keeps the product well-defined when its conditioning set is empty.
        age_given_country = Fraction(0)
    eligible_pairs = age_eligible_pair_count(country_by_year, scenario.max_birth_year_gap)
    all_pairs = world_total * (world_total - 1) // 2
    evidence: EvidenceStatus = "illustrative" if dataset.provenance.kind == "synthetic" else "derived"
    factors = (
        ProbabilityFactor(
            event_id="both_country", label=f"Both people born in {scenario.country_code}",
            probability=both_country,
            denominator=f"C({world_total}, 2) unordered pairs in the imported cohort",
            formula=f"C({country_total}, 2) / C({world_total}, 2)", evidence=evidence,
            source=f"{dataset.provenance.name} · {dataset.provenance.version}",
        ),
        ProbabilityFactor(
            event_id="age_compatible",
            label=f"Birth years within {scenario.max_birth_year_gap} year(s), given both born in {scenario.country_code}",
            probability=age_given_country,
            denominator=f"C({country_total}, 2) target-country pairs",
            formula="eligible target-country pairs / C(target-country births, 2)", evidence=evidence,
            source=f"{dataset.provenance.name} · {dataset.provenance.version}",
            conditioned_on=("both_country",),
        ),
        ProbabilityFactor(
            event_id="meet", label=f"This pair meets ({scenario.meeting_channel})",
            probability=scenario.meeting_probability,
            denominator="Pairs meeting the selected demographic conditions",
            formula="P(meet | both_country, age_compatible)",
            evidence="assumed" if scenario.meeting_probability is not None else "unknown",
            source="User-selected scenario assumption" if scenario.meeting_probability is not None else "No pair-specific encounter estimate supplied",
            conditioned_on=("both_country", "age_compatible"), assumption_id="meeting_probability",
        ),
        ProbabilityFactor(
            event_id="relationship", label="A relationship forms after the defined encounter",
            probability=scenario.relationship_probability,
            denominator="Pairs that had the defined encounter",
            formula="P(relationship | meet, prior demographic conditions)",
            evidence="assumed" if scenario.relationship_probability is not None else "unknown",
            source="User-selected scenario assumption" if scenario.relationship_probability is not None else "No relationship-formation estimate supplied",
            conditioned_on=("both_country", "age_compatible", "meet"), assumption_id="relationship_probability",
        ),
    )
    chain = multiply_factors(factors)
    demographic_probability = both_country * age_given_country
    return ScenarioResult(
        scenario=scenario, chain=chain, population_size=world_total,
        target_country_births=country_total, eligible_country_pairs=eligible_pairs,
        all_population_pairs=all_pairs,
        demographic_probability=demographic_probability,
        metadata={"demographic_probability": f"{demographic_probability.numerator}/{demographic_probability.denominator}",
                  "dataset_kind": dataset.provenance.kind},
    )

