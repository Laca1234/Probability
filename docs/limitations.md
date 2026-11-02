# Limitations and next steps

## Limitations that affect interpretation

- The included dataset is synthetic and limited to three countries. It cannot support a real-world probability claim.
- The CSV importer validates syntax, counts, rectangular year coverage, and internal record consistency, but does not verify all ISO identifiers, world coverage, historical border definitions, dataset licensing, or source truth.
- The UI currently analyzes two distinct unordered people from one selected birth-year interval. The numerical engine supports separate cohort distributions, but the interface does not yet expose a two-person cohort builder.
- Birthplace is the only integrated demographic location concept. Childhood residence, migration, urban/rural differences, population grids, and geographic regions are not modeled in the scenario workflow.
- Encounter and relationship probabilities are unknown unless users choose assumptions. There is no universal pair-specific meeting rate in the app.
- Relationship duration/survival, platform exposure, social networks, language, education, work, travel, and platform recommendation systems are not modeled.
- User assumptions have no empirical uncertainty distribution or sensitivity chart yet.
- Monte Carlo only models independent Bernoulli trials. It is a teaching/simulation tool, not a relationship-network simulator or rare-event estimator.
- Reports currently export JSON manifests, Markdown, and formula-safe CSV. PDF, Excel, comparison workbench, and full history/version comparison are not implemented.
- Scenario storage is local but not encrypted. Manual backup/restore and database migrations beyond the initial schema are not implemented.
- The UI is English and uses Qt translation markers, but a complete Hungarian translation has not been produced.
- A one-folder executable and ZIP have been built from the pinned environment; the ZIP extracted and its startup smoke test passed on the development machine. A clean Windows machine or VM test, signed release, SBOM, dependency vulnerability scan, and installer verification remain outstanding.

## Prioritized follow-up work

1. Import a versioned, redistributable global births series and document its full definitions, coverage, license, code lists, and transformations.
2. Add separate cohorts for the two people and subnational region/childhood-residence distributions where defensible data exists.
3. Add uncertainty/sensitivity plots and alternative dataset/model comparison.
4. Finish localization, keyboard/screen-reader verification, and multi-DPI visual QA.
5. Verify the Windows distribution on a clean machine, then add an installer, SBOM, dependency vulnerability scan, and signed release if needed.
6. Add robust migrations, user-controlled backup/restore, and optional OS-protected encryption if demand justifies it.

