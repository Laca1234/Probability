# Implementation plan and progress

## Workspace inspection

The repository was empty except for Git metadata; no existing application files or tests were overwritten. The final build used a clean Windows x64 Python 3.13.9 environment installed from `requirements-lock.txt`: PySide6/Qt 6.11.1, NumPy 2.3.4, PyInstaller 6.20.0, and hooks-contrib 2026.5. `pip check` passed. Pytest, Hypothesis, Ruff, and mypy were not installed during initial inspection. The first release uses standard-library `unittest` so its core tests need no extra test framework.

## Architecture

```text
QML desktop UI
    ↓ typed Qt slots / properties
application controller and use cases
    ↓
domain records and validation → statistics engine
    ↓                         ↘ NumPy simulation
CSV provenance/import             local SQLite repository
    ↓                              ↓
safe exports ← reproducibility manifest
```

Dependency direction: `ui → application → domain/statistics/data/storage/security`. The mathematical engine has no Qt imports. UI state and file dialogs are kept in the controller. Imported values are parsed as data and are never executed.

## Delivery phases and acceptance criteria

| Phase | Acceptance criteria | Status |
|---|---|---|
| Inspect and plan | Record existing files, environment, dependency graph, scope | Complete |
| Specify mathematics | Define sampling frame, denominators, conditional order, missing-data behavior and reference examples | Complete in `mathematical_model.md` |
| Statistical core | Recurrence, exact pairs, age weighting, hierarchical weights, geodesic helper, validation and tests | Implemented; 29 tests passing |
| Data pipeline | Provenance and hash, safe import, validation, offline teaching dataset | Implemented for CSV imports and synthetic teaching data; no official births bundle integrated |
| Desktop interface | Guided story builder, result decomposition, recurrence, data explorer, simulation, scenario list and settings | Implemented in Qt Quick; source and packaged QML load in offscreen smoke checks; manual DPI and keyboard QA remain |
| Advanced models | Geography, encounter studies, survival models, uncertainty and sensitivity | Deferred where evidence/model is unavailable; only geodesic helper and explicit assumption inputs exist |
| Privacy and security | Local-only storage, safe import/export, threat model, no telemetry | Implemented baseline and documented; database is not encrypted |
| Packaging | Reproducible Windows build spec, build and verify executable | Built from the clean locked environment; ZIP extracted and smoke-tested with QML/database checks on the development machine; clean VM remains |
| Final QA | Run full tests, inspect QML load, type/lint/dependency checks, packaged startup | 29 unit/integration tests, Ruff, mypy, and source/packaged startup smoke checks pass; clean-VM, installer, SBOM, and vulnerability-scan checks remain |

## Main dependencies

1. Exact input validation and the dataset model are prerequisites for all demographic results.
2. The chain-rule factor graph depends on stable event IDs and conditional denominator definitions.
3. The desktop results and saved manifest consume the statistical result; they do not reimplement its arithmetic.
4. Packaging depends on verifying QML module/resource collection and the bundled teaching dataset path.
5. Real-world demographic conclusions depend on provenance, coverage, definitions, and redistribution rights for each future dataset.

## First-release scope

The release provides an end-to-end desktop foundation, not the full breadth of the master prompt. It prioritizes a defensible probability chain, offline demonstration, data import, local persistence, recurrence education, and reproducibility. It deliberately does not claim a real-world “odds of us” result from synthetic data or unsupported encounter statistics.

