# Contributing

Keep the statistical engine independent from Qt. Add a mathematical definition and denominator before implementing a new model factor. New probability factors need stable event IDs, valid dependencies, a source/evidence label, and a hand-checkable test. Never label an assumption as measured data.

Use Python 3.12 or 3.13. Install `requirements.txt` for runtime work or `requirements-dev.txt` for optional tooling. Run the `unittest` command in `docs/testing.md` before submitting a change. For dataset changes, include provenance, redistribution terms, integrity hashes, missing-data policy, transformations, and validation evidence. Do not commit personal scenario data, local databases, secrets, generated `dist/` artifacts, or downloaded datasets without documented rights.

Please use focused changes, readable names, type hints at module boundaries, and explicit error messages. Security reports should follow `SECURITY.md`.

