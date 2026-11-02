# Threat model

The application is local-first and has no service endpoint. The primary trust boundary is user-selected files and local scenario storage.

| Threat | Likelihood / impact | Mitigation in this release | Residual risk / verification |
|---|---|---|---|
| Oversized or malformed CSV | Medium / app crash or memory use | 20 MiB and 200,000-row caps, strict UTF-8/schema checks, bounded field sizes, validation before activation | Parser fuzzing and Windows file-dialog testing remain desirable |
| Duplicate/inconsistent records | Medium / biased probabilities | Duplicate country-year and inconsistent labels rejected; totals are not normalized silently | Source coverage, code identity, historical borders, and statistical anomalies need human review |
| Malicious CSV formulas | Low / spreadsheet actions after export | Export cells that begin with formula characters are apostrophe-prefixed | Spreadsheet applications differ; inspect exports before external sharing |
| Corrupt or hostile JSON/database | Low / app errors or data loss | JSON only, bounded SQLite fields, parameterized SQL, schema version and SQLite integrity check | No automated recovery/backup tool or encrypted storage yet |
| Path traversal or executable import | Low / arbitrary file write/execute | CSV only; no archive extraction, pickle, eval, or downloaded code; imported CSV copied using an internal hash filename | Native file-dialog path behavior still needs packaged Windows QA |
| Local disclosure of scenario data | Medium / privacy loss | Per-user LocalAppData, no network transmission, minimal fields | Not encrypted at rest; compromised Windows account can read data |
| Dependency compromise | Low / code execution | Dependencies are pinned; no automatic updates | SBOM and vulnerability scan are not yet generated; review licenses and hashes before release |
| Dataset-source compromise or misuse | Medium / invalid results | Provenance field, SHA-256, visible evidence labels, no auto-download | Hash proves file identity only, not source truth or correctness |
| Unexpected telemetry | Low / privacy loss | No analytics, account, upload, or update code | Verify packaged build and dependencies before each release |
| Resource exhaustion in simulation | Low / UI slowdown | Worker thread, cancellation event, chunking, 50 million trial maximum | Benchmark on low-memory Windows devices |

Security reporting instructions are in `SECURITY.md`. No claim of perfect security is made.

