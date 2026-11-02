# User guide

## Start

Open the application and note the dataset banner. The bundled dataset is synthetic. Use **Demographics → Import CSV** to load a compatible births file. A provenance form asks for dataset name, publisher, source URL, license, and whether the source is original, derived, estimated, or unknown. Unknown fields can remain “Not supplied”; the app does not fetch the URL. Imported data and its metadata remain local and active after a restart. The app runs offline and does not contact the dataset publisher.

## Build an analysis

1. Choose the target birthplace country and a birth-year interval.
2. Set the largest allowed birth-year difference. The rule uses years only and does not claim exact age in days.
3. Optionally provide a per-pair meeting probability and a relationship probability conditional on that meeting. Blank means unknown. A value you enter is labeled an assumption; the app does not validate it against a study.
4. Choose a meeting-channel label for the report.
5. Calculate. Review the sample population, pair denominator, each conditional factor, evidence label, warning, and manifest ID.
6. Save a named scenario locally or export JSON, Markdown, or CSV.

The displayed demographic factor is for pairs in the selected dataset coverage. If your imported file omits countries or contains inconsistent sources, the result is not a global share.

## Recurrence calculator

Enter `p`, the probability of success per attempt, a number of attempts `N`, and a target percent. Results assume independent trials with unchanged `p`. The warning explains why an individual birth or an overlapping pair count is not automatically an attempt.

## Simulation lab

Enter a Bernoulli probability, trial count (up to 50 million), and non-negative seed. The work runs in a background Qt thread and can be canceled. The interval describes simulation error only. If no simulated successes occur, the app reports an upper bound and does not call the event impossible.

## Teaching tools

Bayes' theorem requires a prior, sensitivity, and false-positive rate. The birthday tool assumes uniform independent draws. The pair count is `N(N−1)/2` unique unordered pairs and is explicitly not an independence model.

## Files and local data

Saved scenarios and the theme preference are in the local SQLite database under `%LOCALAPPDATA%\ProbabilityOfUs`. Imported CSV copies are content-hash named below that folder. Exports are created only after the user chooses a path. The app does not currently encrypt these files.

