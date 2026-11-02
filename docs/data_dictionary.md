# Data dictionary

## Birth-count CSV

| Column | Type | Meaning | Validation |
|---|---|---|---|
| `country_code` | text | ISO 3166-1 alpha-3 code for a country | Uppercase three-letter ASCII syntax; common aggregates are rejected; full code-list validation is not bundled |
| `country_name` | text | Display label from the source | Required; same code must retain one label per file |
| `continent` | text | Geographic grouping used only for hierarchical checks | Required; same code must retain one grouping per file |
| `year` | integer | Calendar birth year | Integer from 1 through 9999 |
| `births` | integer | Birth count for that country-year record | Non-negative integer |

CSV import is UTF-8 (optional BOM), at most 20 MiB and 200,000 records, with exactly the header shown in the README. Duplicate `(country_code, year)` rows and common aggregate rows are rejected. Each listed country must have one row for every year represented in the file; missing years are not filled or imputed. No total is forced to agree with a world total.

## Provenance record

`dataset_id`, `name`, `publisher`, `source_url`, `accessed_on`, `reference_period`, `license`, `version`, `sha256`, `kind`, and `limitations`. The UI asks for publisher, source URL, license, and whether the source is original, derived, estimated, or unknown. Unknowns remain explicitly “Not supplied.”

## Scenario input

Country code, start/end birth year, maximum absolute birth-year gap, optional per-pair meeting probability, optional relationship-given-meeting probability, selected channel label, dataset identifier, and a user-provided scenario name. No exact birth dates, names, addresses, or coordinates are requested.

## Manifest result

Model/application versions, UTC timestamp, input values, dataset identity and hash, computation method, each factor's event ID, exact conditional probability, evidence status, denominator, formula, dependencies, assumption ID, demographic probability, complete story probability if known, software/platform metadata, and simulation seed/budget fields (null for a deterministic analysis).

