# Data sources and provenance

## Bundled dataset

`src/probability_of_us/data/births_teaching_sample.csv` is an author-created synthetic teaching file. Its values are arbitrary small counts for HUN, AUT, and USA in 2015–2019. It has no external source URL, no historical or national-statistics meaning, and no global coverage. It is released as CC0-1.0. It exists so the app can run and the pair calculations can be inspected offline. The file hash is calculated on load and shown in the UI and manifest.

## Candidate real demographic sources

These sources are references for future integrations; the app does not currently download or bundle their birth counts.

- The [United Nations World Population Prospects 2024](https://population.un.org/wpp) provides official estimates and projections with selected country and regional indicators from 1950–2100. Confirm the exact variable definition, country/area coverage, data-file license, and redistribution terms before bundling any extract.
- The [Hungarian Central Statistical Office annual live-birth table](https://www.ksh.hu/stadat_files/nep/en/nep0006.html) is a relevant source for Hungarian totals. Its metadata and territorial definitions must be checked before joining it to international series.
- The [Population Reference Bureau article on cumulative human births](https://www.prb.org/news/how-many-people-have-ever-lived-on-earth/) reports an estimate based on assumptions about prehistoric population, fertility, and the timeline of Homo sapiens. Its publication context is 2022; it is not a current headcount and is not integrated as a model denominator.

The source pages were reviewed on 22 October 2026. A source being publicly viewable does not itself grant permission to redistribute its data.

## Import provenance

The CSV parser records an import ID, name, publisher, source URL, access date, observed year range, SHA-256, license, source-data status (original/derived/estimated/unknown), and limitations. The UI asks for this metadata and labels absent provenance as “Not supplied”; it does not infer a source or silently normalize totals. An imported dataset is copied by content hash under the user's local application-data folder after validation, and the selected dataset metadata is persisted locally so it remains active after restart.

The parser checks exact headers, UTF-8, file size, record limit, country-code shape, non-negative integer counts, country-year uniqueness, rectangular country-year coverage, common aggregate-region identifiers, and consistent country name/continent labels. It does not yet verify codes against a bundled complete ISO register, check historical boundary changes, reconcile world totals, or detect statistical outliers. Those checks remain required before an imported source is treated as global coverage.

