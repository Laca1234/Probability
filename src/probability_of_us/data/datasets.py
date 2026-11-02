"""Strict CSV import and integrity metadata for birth-count datasets."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from typing import cast
from datetime import date
from pathlib import Path

from probability_of_us.domain.models import BirthDataset, BirthRecord, DatasetKind, DatasetProvenance, ModelInputError

REQUIRED_COLUMNS = ("country_code", "country_name", "continent", "year", "births")
MAX_DATASET_BYTES = 20 * 1024 * 1024
MAX_RECORDS = 200_000
MAX_FIELD_CHARS = 256
AGGREGATE_CODES = frozenset({
    "WLD", "AFR", "ARB", "CSS", "EAP", "EAS", "ECA", "ECS", "EMU", "EUU", "HIC", "HPC",
    "LAC", "LCN", "LDC", "LIC", "LMC", "LMY", "MEA", "MIC", "MNA", "NAC", "OED", "OSS",
    "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST", "UMC", "WBG", "WLD",
})
AGGREGATE_NAMES = frozenset({"world", "world total", "worldwide", "all countries", "global"})


def load_birth_csv(
    path: str | Path,
    *,
    dataset_id: str | None = None,
    dataset_name: str | None = None,
    publisher: str = "User imported",
    source_url: str = "Not supplied",
    license_text: str = "Not supplied; verify before redistribution",
    version: str = "user-import-1",
    kind: str = "unknown",
) -> BirthDataset:
    file_path = Path(path)
    if file_path.suffix.lower() != ".csv":
        raise ModelInputError("Only documented CSV datasets are supported.")
    size = file_path.stat().st_size
    if size <= 0 or size > MAX_DATASET_BYTES:
        raise ModelInputError(f"CSV file must be between 1 byte and {MAX_DATASET_BYTES // (1024 * 1024)} MB.")
    with file_path.open("rb") as stream:
        raw = stream.read(MAX_DATASET_BYTES + 1)
    if len(raw) > MAX_DATASET_BYTES:
        raise ModelInputError(f"CSV file exceeds the {MAX_DATASET_BYTES // (1024 * 1024)} MB limit.")
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ModelInputError("CSV must use UTF-8 or UTF-8 with a byte-order mark.") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    headers = tuple(reader.fieldnames or ())
    if headers != REQUIRED_COLUMNS:
        raise ModelInputError("CSV header must be exactly: " + ",".join(REQUIRED_COLUMNS))
    records: list[BirthRecord] = []
    try:
        for line_number, row in enumerate(reader, start=2):
            if line_number > MAX_RECORDS + 1:
                raise ModelInputError(f"CSV exceeds the {MAX_RECORDS:,}-record limit.")
            if None in row or any(value is None for value in row.values()):
                raise ModelInputError(f"Malformed or incomplete CSV row at line {line_number}.")
            if any(len(value) > MAX_FIELD_CHARS for value in row.values()):
                raise ModelInputError(f"CSV field is too long at line {line_number}.")
            code = row["country_code"].strip().upper()
            if not re.fullmatch(r"[A-Z]{3}", code):
                raise ModelInputError(f"Invalid country code at line {line_number}: {code!r}.")
            if code in AGGREGATE_CODES or row["country_name"].strip().casefold() in AGGREGATE_NAMES:
                raise ModelInputError(f"Aggregate region row is not a country record at line {line_number}: {code}.")
            if not row["year"].strip().isdigit() or not row["births"].strip().isdigit():
                raise ModelInputError(f"Year and births must be non-negative integers at line {line_number}.")
            records.append(BirthRecord(
                country_code=code,
                country_name=row["country_name"].strip(),
                continent=row["continent"].strip(),
                year=int(row["year"]),
                births=int(row["births"]),
            ))
    except csv.Error as exc:
        raise ModelInputError(f"Malformed CSV: {exc}") from exc
    if not records:
        raise ModelInputError("CSV contains no records.")
    # Names and geographic classifications should remain consistent across time.
    country_labels: dict[str, tuple[str, str]] = {}
    for record in records:
        label = (record.country_name, record.continent)
        if record.country_code in country_labels and country_labels[record.country_code] != label:
            raise ModelInputError(f"Country {record.country_code} changes name or continent classification in the file.")
        country_labels[record.country_code] = label
    dataset_kind = cast(DatasetKind, kind) if kind in {"original", "derived", "estimated", "synthetic", "unknown"} else "unknown"
    return BirthDataset(
        tuple(records),
        DatasetProvenance(
            dataset_id=dataset_id or f"import-{digest[:12]}",
            name=dataset_name or file_path.stem,
            publisher=publisher.strip() or "Not supplied",
            source_url=source_url.strip() or "Not supplied",
            accessed_on=date.today().isoformat(),
            reference_period=f"{min(r.year for r in records)}–{max(r.year for r in records)}",
            license=license_text.strip() or "Not supplied; verify before redistribution",
            version=version,
            sha256=digest,
            kind=dataset_kind,
            limitations=("Country code syntax is checked; external ISO register validation is not bundled.",
                         "Coverage completeness and source definitions must be verified by the importer."),
        ),
    )


def validate_dataset_totals(dataset: BirthDataset) -> tuple[str, ...]:
    """Return data-quality warnings without silently normalizing input totals."""
    warnings: list[str] = []
    yearly: dict[int, int] = {}
    for record in dataset.records:
        yearly[record.year] = yearly.get(record.year, 0) + record.births
    if len(dataset.countries) < 2:
        warnings.append("Only one country is covered; world or regional shares cannot be estimated.")
    warnings.append("Yearly sums are totals for the imported coverage; they are not treated as world totals.")
    if dataset.provenance.kind == "synthetic":
        warnings.append("Synthetic values are for teaching only and are not observed demographic counts.")
    if dataset.provenance.kind == "unknown":
        warnings.append("Source-data status is unknown; check provenance before interpreting the calculated ratios.")
    return tuple(warnings)

