# Probability of Us

**A privacy-first desktop laboratory for demographic and relationship probability models.**

Probability of Us is a native desktop application that explores how demographic conditions, probability theory, and user-defined assumptions can be combined into a transparent mathematical model.

The application provides exact demographic pair calculations, conditional probability decomposition, recurrence analysis, Monte Carlo simulation, and local scenario management — all without requiring an internet connection.

> **Important:** Probability of Us is an educational and exploratory tool, not a predictive dating service. Its bundled dataset is synthetic, and user-provided encounter or relationship probabilities are assumptions rather than empirical findings.

## Overview

Probability of Us explores a mathematical question: how can a sequence of demographic and hypothetical conditions be combined into a probability model?

Instead of presenting a single unexplained number, the application breaks the calculation into conditional factors. Each factor has an identifiable event, denominator, formula, evidence status, and dependencies.

The result is a transparent calculation that users can inspect, save, reproduce, and export.

## Features

### Demographic probability analysis
- Calculate the probability of selecting two distinct people born in a selected target country.
- Define a birth-year interval and an allowed birth-year difference.
- Calculate unordered pairs without replacement.
- Use exact rational arithmetic for count-derived probabilities.
- Inspect conditional factors and their denominators.

### Conditional relationship model
- Build a multi-stage probability chain.
- Add optional meeting and relationship assumptions.
- Keep unknown factors explicitly unknown instead of inventing values.
- Track the evidence status and dependencies of individual factors.
- Generate a calculation manifest for reproducibility.

### Probability tools
- Recurrence probability calculator.
- Required-attempt calculations for a target probability.
- Monte Carlo Bernoulli simulation with reproducible seeds.
- Bayesian probability teaching tool.
- Birthday collision calculator.
- Geographic distance utility using the haversine formula.

### Data management
- Import validated birth-count CSV datasets.
- Record dataset provenance and source information.
- Calculate and retain dataset SHA-256 hashes.
- Store scenarios locally.
- Export results as JSON, Markdown, and CSV.

### Privacy-first operation
- Runs offline.
- Does not require registration or an online account.
- Does not send imported datasets or scenarios to a remote service.
- Stores application data locally.
- Does not request personal names, exact birth dates, addresses, or coordinates for the main scenario workflow.

## Technology stack

| Component | Technology |
|---|---|
| Language | Python 3.12–3.13 |
| Desktop framework | PySide6 |
| UI technology | Qt Quick / QML |
| Numerical computing | NumPy |
| Exact arithmetic | Python `fractions.Fraction` |
| High-precision recurrence | Python `decimal` |
| Local database | SQLite |
| Testing | pytest, Hypothesis |
| Packaging | PyInstaller |
| Build configuration | setuptools / pyproject.toml |

## Getting started

### Requirements

- Windows, Linux, or another supported Python desktop environment.
- Python 3.12 or 3.13.
- pip.
- A working Qt-compatible desktop environment.

The Windows packaging guide documents the tested Windows build environment and distribution process.

### Installation

Clone the repository:

```bash
git clone https://github.com/Laca1234/Probability.git
cd Probability
```

Create a virtual environment:

**Windows PowerShell**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### Launch

Run the application using:

```bash
python run_app.py
```

Alternatively, after installation:

```bash
probability-of-us
```

## Running tests

Install the development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest
```

The tests cover probability calculations, model invariants, simulation, data validation, storage, and export behavior.

## Data and mathematical integrity

The application includes a small synthetic teaching dataset covering three countries between 2015 and 2019.

This dataset exists only to demonstrate the application's functionality and make exact calculations easy to inspect. It is not observed or estimated demographic data and must not be interpreted as a representation of real-world populations.

Users can import their own birth-count datasets. Imported files are validated for structure, record consistency, and required fields. The application records provenance information but does not independently verify the truth, completeness, or licensing of external data.

The mathematical model uses distinct, unordered pairs sampled without replacement. It distinguishes demographic probabilities from hypothetical encounter and relationship assumptions.

For more information, see the [mathematical model](docs/mathematical_model.md).

## Project structure

```text
Probability/
├── build/
│   ├── probability_of_us.spec
│   └── ...
├── data/
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── build_windows.md
│   ├── data_dictionary.md
│   ├── data_sources.md
│   ├── limitations.md
│   ├── mathematical_model.md
│   ├── privacy.md
│   ├── testing.md
│   ├── user_guide.md
│   └── ...
├── src/
│   └── probability_of_us/
│       ├── application/
│       ├── assets/
│       ├── data/
│       ├── domain/
│       ├── security/
│       ├── statistics/
│       ├── storage/
│       ├── ui/
│       └── main.py
├── tests/
├── pyproject.toml
├── requirements.txt
├── requirements-lock.txt
├── run_app.py
└── README.md
```

## Documentation

The repository includes additional technical and user-facing documentation:

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | Application layers, data flow, and reproducibility |
| [User guide](docs/user_guide.md) | How to use the application |
| [Mathematical model](docs/mathematical_model.md) | Formulas, assumptions, and probability calculations |
| [Data dictionary](docs/data_dictionary.md) | CSV format and scenario data |
| [Data sources](docs/data_sources.md) | Dataset provenance and source handling |
| [Limitations](docs/limitations.md) | Known limitations and future improvements |
| [Privacy](docs/privacy.md) | Local data handling and privacy |
| [Testing](docs/testing.md) | Testing approach |
| [Windows build guide](docs/build_windows.md) | Building and packaging the Windows application |

## Known limitations

- The bundled dataset is synthetic and cannot support real-world demographic conclusions.
- External dataset coverage and accuracy are not independently verified.
- Encounter and relationship probabilities require user-provided assumptions.
- The model does not represent social networks, migration, relationship duration, or individual behavior.
- Monte Carlo simulation assumes independent Bernoulli trials.
- Local database contents are not currently encrypted.
- A clean Windows machine distribution test and several release-verification steps remain outstanding.

See [Limitations and next steps](docs/limitations.md) for the complete list.

## License

The application source code is distributed under the **MIT License**.

The bundled synthetic teaching data is dedicated to the public domain under **CC0-1.0**. Third-party dependencies have their own licensing terms; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

---

**Probability of Us** is an independent software project focused on transparent calculations, mathematical integrity, reproducibility, and privacy-first desktop software.
