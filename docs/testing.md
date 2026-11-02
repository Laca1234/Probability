# Testing and verification

Run from the repository root:

```powershell
py -3.13 -c "import sys,unittest; sys.path.insert(0, 'src'); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not result.wasSuccessful())"
```

The 29 tests cover recurrence known answers and edges, subnormal probability preservation, exact pair counts, chain dependency and double-count protection, age/cohort weighting, country and hierarchical weighting, geodesic distance, synthetic-data analysis, assumption labeling, strict CSV and duplicate handling, formula-safe export, SQLite persistence across restart, seeded simulation, aggregate and incomplete data rejection, and zero-success interpretation.

The test suite uses the standard library `unittest`; all 29 tests pass. Ruff lint and mypy type checks also pass. Property-based tests, dependency vulnerability scanning, coverage measurement, and UI keyboard tests are not yet part of the first release. The packaged executable and the executable extracted from the final ZIP were launched with the offscreen Qt platform using isolated `LOCALAPPDATA`; each loaded the QML root, exited successfully, and created its SQLite database. This verifies startup on the build machine, not a clean Windows installation.

The QML interface should be checked on Windows at 100%, 150%, and 200% display scaling and with keyboard-only navigation. Package checks should start the actual output folder on a clean Windows user profile, verify import/export and local database behavior, and confirm the packaged synthetic CSV loads without relying on the repository path.

