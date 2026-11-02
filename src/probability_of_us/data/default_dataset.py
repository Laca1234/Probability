"""Load the explicitly synthetic demonstration population."""

from __future__ import annotations

from pathlib import Path

from probability_of_us.data.datasets import load_birth_csv
from probability_of_us.domain.models import BirthDataset, DatasetProvenance


def default_dataset() -> BirthDataset:
    path = Path(__file__).resolve().parent / "births_teaching_sample.csv"
    if not path.exists():
        # Source-checkout fallback before wheel/package data has been installed.
        path = Path(__file__).resolve().parents[3] / "data" / "births_teaching_sample.csv"
    dataset = load_birth_csv(
        path,
        dataset_id="synthetic-teaching-v1",
        dataset_name="Three-country synthetic teaching population",
        publisher="Probability of Us contributors",
        source_url="Not applicable; author-created synthetic values",
        license_text="CC0 for the synthetic teaching values; application code is MIT licensed",
        version="1.0.0",
        kind="synthetic",
    )
    return BirthDataset(dataset.records, DatasetProvenance(
        dataset_id=dataset.provenance.dataset_id,
        name=dataset.provenance.name,
        publisher=dataset.provenance.publisher,
        source_url=dataset.provenance.source_url,
        accessed_on=dataset.provenance.accessed_on,
        reference_period=dataset.provenance.reference_period,
        license=dataset.provenance.license,
        version=dataset.provenance.version,
        sha256=dataset.provenance.sha256,
        kind="synthetic",
        limitations=("Toy counts, not observed births.", "Covers only Hungary, Austria, and the United States.",
                     "The three-country total is not a world population denominator.",
                     "Do not interpret outputs as estimates about real people."),
    ))

