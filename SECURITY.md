# Security policy

## Reporting

Do not include private scenario data in a report. For a vulnerability, provide the affected version, Windows/Python environment, reproduction steps using synthetic data, impact, and any safe mitigation. In this initial repository there is no staffed private disclosure address; report through the repository's configured private security advisory channel if available. If none is available, open a public issue with a minimal non-sensitive description and request a private contact route before sharing exploit details.

## Supported versions

Only the current source version is maintained at this stage. The project does not yet publish signed binaries or a security response SLA.

## Security posture

The app uses bounded CSV parsing, strict JSON exports, parameterized SQLite, formula-safe CSV output, local-only storage, and no automatic network activity. Imported data is untrusted. Scenario files and the local database are not encrypted. See `docs/threat_model.md` and `docs/privacy.md` for residual risks.

