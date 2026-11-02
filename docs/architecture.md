# Architecture

## Layers

- `ui/qml/Main.qml`: native Qt Quick navigation, forms, result explanation, accessibility text, and theme colors. It contains presentation only.
- `application/app_controller.py`: validates Qt inputs, calls use cases, runs simulations on `QThreadPool`, opens user-selected file dialogs, and coordinates storage/export.
- `domain/models.py`: immutable records for births, provenance, scenarios, factors, and results. Domain validation has no Qt dependency.
- `statistics/`: exact rational probability functions, age/cohort calculations, geographic distance, recurrence, model composition, and vectorized simulation.
- `data/`: strict CSV parser, provenance hash, data-quality messages, and the synthetic offline teaching example.
- `storage/`: small SQLite repository using parameterized SQL, bounded JSON payloads, transactions, and a schema version.
- `security/`: atomic bounded exports and spreadsheet formula neutralization.
- `tests/`: standard-library tests for known-answer calculations, invariants, import validation, storage, export, and reproducible simulation.
- `docs/` and `build/`: mathematics, provenance, privacy, threat model, instructions, and packaging configuration.

## Flow

The QML story builder supplies a selected country, year interval, birth-year gap, optional encounter and relationship assumptions, and channel label. The controller constructs a `Scenario`, then calls `statistics.story_model.analyze_story`. The model uses exact integer counts to calculate the first two conditional factors and preserves unknown later factors as `None`. The UI displays every factor's conditional meaning, denominator, evidence label, and source. The calculation manifest records those same values and the dataset hash.

## Reproducibility

Demographic calculations use integer pair counts and `fractions.Fraction`. Recurrence uses `log1p`/`expm1`, with Decimal arithmetic for inputs below the float range. Simulations use NumPy's `default_rng(seed)` and report the seed, budget, observed successes, interval, and limitations. A saved scenario stores JSON-serializable inputs and a manifest; it does not store personal names or exact dates.

## Runtime storage

The default database path is `%LOCALAPPDATA%\ProbabilityOfUs\probability_of_us.sqlite3`; validated import copies are stored under `%LOCALAPPDATA%\ProbabilityOfUs\datasets\<sha256>.csv`. Users can delete these files by deleting the app data folder after closing the app. The application does not currently encrypt them or implement migration rollback beyond SQLite's schema version check.

