# Probability of Us — Technical Documentation

## 1. Project overview

Probability of Us is a privacy-first desktop application designed to explore demographic and relationship probability models through transparent mathematical calculations.

The application combines demographic pair analysis with conditional probability decomposition and optional user-defined assumptions. It also provides independent probability utilities, simulation tools, local scenario storage, and structured result exports.

The central design principle is mathematical transparency: the application should not present a probability as an unexplained result. Its calculations should be traceable to their inputs, denominators, formulas, assumptions, and data sources.

### 1.1 Project objectives

- Provide an accessible desktop interface for probability analysis.
- Calculate demographic probabilities using exact arithmetic where possible.
- Separate demographic evidence from hypothetical assumptions.
- Preserve unknown probabilities instead of silently estimating them.
- Make calculations reproducible through structured manifests.
- Keep user data and imported datasets on the local machine.
- Provide useful exports for further inspection.

### 1.2 Intended use

The application is intended for educational, mathematical, and exploratory use.

It is not a dating application, a matchmaking system, a demographic forecasting service, or a scientifically validated model of individual relationships.

---

## 2. Technology stack

| Layer | Technology |
|---|---|
| Programming language | Python 3.12–3.13 |
| Desktop framework | PySide6 6.11.1 |
| UI | Qt Quick / QML |
| Numerical computing | NumPy 2.3.4 |
| Exact probability arithmetic | `fractions.Fraction` |
| High-precision calculations | `decimal.Decimal` |
| Local persistence | SQLite |
| Build system | setuptools |
| Packaging | PyInstaller 6.20.0 |
| Testing | pytest, Hypothesis |
| Code quality | Ruff, mypy |

The runtime dependencies are pinned in `requirements.txt` and `requirements-lock.txt`. Project configuration and optional development dependencies are defined in `pyproject.toml`.

---

## 3. Application architecture

The application follows a layered architecture. Presentation, application coordination, domain models, mathematical calculations, data handling, persistence, and export security are separated.

### 3.1 User interface layer

Location:

`src/probability_of_us/ui/qml/`

The Qt Quick interface provides the application's navigation, forms, result presentation, explanatory text, and theme-related UI elements.

The interface is responsible for presenting information and collecting user input. Mathematical calculations are delegated to the underlying application and statistics layers.

### 3.2 Application layer

Location:

`src/probability_of_us/application/`

Main controller:

`app_controller.py`

The application controller coordinates the interface and the underlying services.

Its responsibilities include:

- Validating incoming UI values.
- Constructing scenario objects.
- Calling mathematical use cases.
- Coordinating dataset imports.
- Managing scenario persistence.
- Opening user-selected file dialogs.
- Coordinating result exports.
- Running longer simulations through Qt background workers.
- Returning calculation results and validation messages to the interface.

### 3.3 Domain layer

Location:

`src/probability_of_us/domain/`

Main module:

`models.py`

The domain layer contains immutable records and validation rules for the application's core concepts.

These include:

- Birth-count records.
- Dataset provenance.
- Scenario inputs.
- Probability factors.
- Analysis results.

Domain validation is designed to remain independent of Qt.

### 3.4 Statistics layer

Location:

`src/probability_of_us/statistics/`

Main modules:

- `demography.py`
- `probability.py`
- `simulation.py`
- `story_model.py`

This layer contains the mathematical implementation.

It handles demographic pair calculations, probability operations, recurrence, simulation, and the composition of conditional probability factors.

Exact rational arithmetic is used for count-derived probabilities where appropriate. NumPy is used for vectorized simulation.

### 3.5 Data layer

Location:

`src/probability_of_us/data/`

Main modules:

- `datasets.py`
- `default_dataset.py`
- `births_teaching_sample.csv`

This layer loads and validates demographic CSV files, handles dataset provenance, calculates data hashes, and provides the bundled synthetic example.

### 3.6 Storage layer

Location:

`src/probability_of_us/storage/`

Main module:

`repository.py`

The storage layer provides local SQLite persistence for application scenarios and related records.

It uses parameterized SQL, transactions, bounded JSON payloads, and a schema version check.

### 3.7 Security and export layer

Location:

`src/probability_of_us/security/`

Main module:

`exports.py`

The export layer provides controlled file output, including bounded and atomic export operations and spreadsheet formula neutralization for CSV output.

---

## 4. Application execution flow

The main package entry point is:

`src/probability_of_us/main.py`

The root-level `run_app.py` provides a convenient launcher.

The general analysis flow is:

1. The user opens the application.
2. The application loads its available dataset.
3. The user selects a target country and birth-year interval.
4. The user defines the maximum allowed birth-year difference.
5. Optional encounter and relationship assumptions can be supplied.
6. The controller validates the inputs and constructs a scenario.
7. The statistics layer performs the calculation.
8. The result is returned with conditional factors and supporting metadata.
9. The user can inspect, save, or export the result.

The interface does not independently calculate the mathematical result. The controller coordinates the operation and the statistics layer owns the calculation logic.

---

## 5. Mathematical model

### 5.1 Sampling frame

The demographic model uses a selected dataset and birth-year interval as its sampling frame.

Let:

- `B(c, y)` represent the number of births recorded for country `c` in year `y`.
- `N` represent the total number of represented births across the selected interval.
- `Nₜ` represent the number of births in the selected target country.

The total number of possible unordered pairs of distinct people is:

```text
C(N, 2) = N(N - 1) / 2
```

The probability that both selected people belong to the target country is:

```text
P(both target-country births) = C(Nₜ, 2) / C(N, 2)
```

This calculation assumes two distinct people are selected without replacement.

The result describes the dataset's represented population. It can only be interpreted as a global share if the underlying dataset consistently covers global births for every selected year.

### 5.2 Birth-year compatibility

Let `nᵧ` represent the number of target-country births in year `y`, and let `d` be the maximum permitted birth-year difference.

The number of eligible pairs is:

```text
eligible pairs =
    Σᵧ C(nᵧ, 2)
    + Σᵧ<z, z-y≤d nᵧ × n_z
```

The conditional probability of satisfying the birth-year rule is:

```text
P(gap ≤ d | both target-country births) =
    eligible pairs / C(Nₜ, 2)
```

The application uses birth years, not exact birth dates. Therefore, this condition does not establish an exact age difference in days.

### 5.3 Conditional relationship chain

The implemented story model separates the analysis into conditional factors:

```text
P(both target-country births)
× P(compatible birth years | both target-country births)
× P(this pair meets | both demographic events)
× P(relationship forms | meeting and prior conditions)
```

The first demographic factors can be calculated from the selected dataset.

The meeting and relationship factors are optional assumptions supplied by the user. If either is unknown, the complete story probability remains unknown.

This distinction is important: the application does not invent an encounter probability or derive a relationship probability from unrelated survey statistics.

Each factor records its event identifier, formula, denominator, evidence status, source, and dependencies. Invalid dependencies and repeated event identifiers are rejected to avoid double counting.

### 5.4 Exact arithmetic

Count-derived probabilities use Python's `fractions.Fraction` to preserve exact numerator and denominator values.

This avoids unnecessary floating-point rounding during demographic calculations.

Recurrence calculations use numerically stable functions such as `log1p` and `expm1`. Decimal arithmetic is used for values that fall below the representable floating-point range.

A mathematically exact fraction is exact under the selected dataset and sampling assumptions. It does not automatically mean the result is an accurate representation of the real world.

---

## 6. Additional probability utilities

The application includes several calculations beyond the main demographic scenario workflow.

### 6.1 Independent probability

For two independent events:

```text
P(A and B) = P(A) × P(B)
```

When selecting two distinct people from the same finite population without replacement, the appropriate finite-population pair calculation must be used instead of assuming independent selections.

### 6.2 Recurrence

The recurrence calculator implements:

```text
P(at least one success) = 1 - (1 - p)^N
```

Where:

- `p` is the probability of success per attempt.
- `N` is the number of attempts.

This assumes independent attempts with a constant probability.

The required number of attempts to reach a target probability `q` is:

```text
N = ceil(ln(1 - q) / ln(1 - p))
```

Special cases are handled explicitly. For example, a positive target is unreachable when `p = 0`.

The application does not treat every possible birth pair as an independent attempt.

### 6.3 Monte Carlo simulation

The simulation module uses NumPy's random number generator:

`default_rng(seed)`

The simulation is based on Bernoulli trials and provides reproducible results when the same seed and inputs are used.

The interface supports a trial budget of up to 50 million and allows the user to cancel the operation.

The reported interval represents Monte Carlo sampling error. It does not represent uncertainty in the demographic dataset or the mathematical model.

### 6.4 Bayesian teaching tool

The application includes a Bayes' theorem calculator:

```text
P(H | +) =
    P(+ | H) × P(H)
    -----------------------------------------------
    P(+ | H) × P(H) + P(+ | not H) × P(not H)
```

It requires a prior probability, sensitivity, and false-positive rate.

### 6.5 Birthday collision calculation

The birthday tool demonstrates collision probability under independent, uniformly distributed categorical draws.

### 6.6 Geographic distance

The geographic utility uses the haversine formula and a mean Earth radius of 6,371.0088 km.

It calculates great-circle distance and does not model roads, borders, migration, population density, or actual travel distance.

---

## 7. Dataset management

### 7.1 Bundled teaching dataset

The application includes:

`src/probability_of_us/data/births_teaching_sample.csv`

The dataset contains arbitrary small integer counts for three countries across 2015–2019.

It exists exclusively for offline demonstration and testing.

It is not observed or estimated demographic data and must not be used to support real-world demographic conclusions.

The synthetic values are dedicated to the public domain under CC0-1.0.

### 7.2 CSV import format

The expected birth-count CSV contains the following columns:

| Column | Meaning |
|---|---|
| `country_code` | ISO 3166-1 alpha-3 country code syntax |
| `country_name` | Country display name |
| `continent` | Geographic grouping |
| `year` | Calendar birth year |
| `births` | Non-negative integer birth count |

The importer applies structural and consistency checks.

These include:

- UTF-8 encoding, with optional BOM.
- A maximum file size of 20 MiB.
- A maximum of 200,000 records.
- Required columns and exact header structure.
- Duplicate country/year row rejection.
- Common aggregate row rejection.
- Consistent country labels and geographic groupings.
- Complete year coverage for each listed country.

The importer does not independently verify every ISO identifier, the truth of the source, historical border definitions, or whether the dataset represents the entire world.

### 7.3 Provenance

Imported datasets can be associated with metadata such as:

- Dataset name.
- Publisher.
- Source URL.
- Access date.
- Reference period.
- License.
- Version.
- SHA-256 hash.
- Source classification.
- Limitations.

The application records provenance information but does not fetch the source URL or independently validate the publisher's claims.

---

## 8. Local storage and privacy

The application is designed to operate offline.

The default database location is:

```text
%LOCALAPPDATA%\ProbabilityOfUs\probability_of_us.sqlite3
```

Imported dataset copies are stored below:

```text
%LOCALAPPDATA%\ProbabilityOfUs\datasets\
```

Dataset copies use their SHA-256 hash in the filename.

Saved scenarios contain JSON-serializable inputs and a calculation manifest. They do not require personal names or exact birth dates.

Exports are written only after the user selects a destination.

### 8.1 Privacy characteristics

- No registration or online account is required.
- No remote synchronization is implemented.
- Imported datasets remain local.
- Saved scenarios remain local.
- The application does not require internet access for its normal operation.

### 8.2 Storage limitations

Local data is not currently encrypted.

Users can remove local application data by closing the application and deleting the `ProbabilityOfUs` folder from LocalAppData.

The application does not currently provide a complete built-in backup and restore workflow.

See `docs/privacy.md` for additional details.

---

## 9. Exports and reproducibility

The application supports:

- JSON calculation manifests.
- Markdown reports.
- CSV exports.

A calculation manifest can record:

- Application and model versions.
- UTC timestamp.
- Scenario inputs.
- Dataset identity and hash.
- Calculation method.
- Conditional factors.
- Exact probability values.
- Denominators and formulas.
- Evidence statuses.
- Factor dependencies.
- Assumption identifiers.
- Simulation seed and trial budget, when applicable.

The purpose is to make a calculation inspectable and reproducible rather than treating the displayed result as an isolated number.

CSV output includes spreadsheet formula neutralization to reduce the risk of exported text being interpreted as executable spreadsheet formulas.

---

## 10. Testing and quality assurance

The project uses pytest and Hypothesis for testing.

The test suite is located in:

`tests/`

Current test modules include:

- `test_application_controller.py`
- `test_data_storage_security.py`
- `test_demography.py`
- `test_probability.py`
- `test_simulation.py`
- `test_story_model.py`

The tests cover mathematical known-answer cases, invariants, data import validation, local storage, export behavior, and reproducible simulation.

To run the tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Ruff and mypy are included as development dependencies for code quality and static analysis.

---

## 11. Installation and development

### Requirements

- Python 3.12 or 3.13.
- pip.
- A supported Qt desktop environment.

### Create a virtual environment

Windows:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### Install

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### Launch

```bash
python run_app.py
```

Alternatively:

```bash
probability-of-us
```

### Development installation

```bash
python -m pip install -e ".[dev]"
```

### Run tests

```bash
python -m pytest
```

---

## 12. Windows packaging

The project includes a PyInstaller configuration:

`build/probability_of_us.spec`

The documented Windows build environment uses Windows x64 and Python 3.13.

The pinned build environment is defined in `requirements-lock.txt`.

A typical clean build sequence is:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --requirement requirements-lock.txt
py -m PyInstaller --noconfirm --clean build/probability_of_us.spec
```

The expected one-folder application location is:

```text
dist\ProbabilityOfUs\ProbabilityOfUs.exe
```

The application stores mutable data outside the distribution directory, under LocalAppData.

A successful build should not be assumed until the packaged application has been launched and the required functionality has been checked.

The repository's Windows build guide documents QML resources, Qt plugins, packaging checks, licensing considerations, and release verification.

---

## 13. Known limitations

The current implementation has several important limitations:

1. The bundled demographic dataset is synthetic and limited to three countries.
2. External dataset coverage, accuracy, licensing, and source truth are not independently verified.
3. The main scenario interface analyzes two distinct unordered people from one selected birth-year interval.
4. Childhood residence, migration, population density, and social networks are not integrated into the main workflow.
5. Meeting and relationship probabilities remain unknown unless users provide assumptions.
6. Relationship duration and survival are not modeled.
7. User assumptions do not currently have empirical uncertainty distributions or sensitivity charts.
8. Monte Carlo simulation models independent Bernoulli trials, not relationship networks.
9. PDF and Excel exports are not implemented.
10. Local scenario storage is not encrypted.
11. Full backup and restore functionality is not implemented.
12. A complete Hungarian translation is not available.
13. Clean-machine Windows verification, signed release preparation, SBOM generation, and dependency vulnerability scanning remain outstanding.

These limitations are part of the model's interpretation and should be considered when evaluating any result.

---

## 14. Future development

Potential development directions documented by the project include:

- Integrating a versioned, redistributable global birth dataset.
- Supporting separate demographic cohorts for both people.
- Adding defensible subnational and regional demographic data.
- Introducing uncertainty and sensitivity visualizations.
- Supporting comparison between datasets and model configurations.
- Completing localization and accessibility verification.
- Improving backup, restore, and database migration support.
- Verifying Windows packaging on clean machines.
- Adding an SBOM and dependency vulnerability scanning to the release workflow.

These are development directions, not claims that the features are already implemented.

---

## 15. Repository documentation

The project contains additional documentation under `docs/`.

| File | Purpose |
|---|---|
| `architecture.md` | Internal application architecture and data flow |
| `build_windows.md` | Windows build and release process |
| `data_dictionary.md` | Dataset and scenario field definitions |
| `data_sources.md` | Data source and provenance information |
| `distribution_readme.md` | Distribution package information |
| `implementation_plan.md` | Implementation planning |
| `limitations.md` | Known limitations and future work |
| `mathematical_model.md` | Detailed formulas and mathematical assumptions |
| `privacy.md` | Local storage and privacy considerations |
| `testing.md` | Testing documentation |
| `threat_model.md` | Security threat model |
| `user_guide.md` | User-facing application instructions |

---

## 16. License

The application source code is distributed under the MIT License.

The bundled synthetic teaching dataset is dedicated to the public domain under CC0-1.0.

Third-party dependencies retain their respective licenses. Refer to `THIRD-PARTY-NOTICES.md` and the Windows build documentation before redistributing packaged binaries.

---

**Probability of Us** is an independent software project focused on transparent mathematical modeling, exact calculations, reproducibility, and privacy-first desktop application development.
