# Privacy and data handling

## Data inventory

| Data | Purpose | Location | Sent outside device? |
|---|---|---|---|
| Theme preference | Restore the selected appearance | SQLite preferences table | No |
| Saved scenario inputs and manifest | Reopen and reproduce a calculation | SQLite scenarios table | No |
| Imported validated birth CSV and user-entered provenance | Offline calculation and hash-based identification | Local `datasets` directory and SQLite active-dataset preference | No |
| Temporary export file | Atomic report writing | Same folder chosen by user, briefly | No |
| Simulation input and result | Current application session | Memory unless user saves/exports | No |

The UI asks only for coarse country and birth-year information and optional model assumptions. It does not ask for names, precise birth dates, addresses, or contact details. There is no telemetry, analytics SDK, account, cloud sync, crash upload, automatic update check, advertising, or background upload. Source links open only when the user clicks them.

## Storage and deletion

Data is stored under `%LOCALAPPDATA%\ProbabilityOfUs`, using the current Windows user's normal filesystem permissions. This release does not encrypt the database, does not implement database backup/restore, and does not guarantee secure deletion. Close the app and delete that folder to remove its database and imported files. Keep report exports in mind when cleaning up sensitive information.

## Export

Reports include model, inputs, exact or unknown factor values, source/hash details, assumptions, and limitations. Do not include identifying details in scenario names or notes. CSV formula-leading strings are prefixed to reduce spreadsheet formula injection risk. Export is atomic within the chosen target directory where the filesystem allows atomic replacement.

## Network behavior

The current executable has no application code that contacts the network. The source links are opened only by a user action and can disclose ordinary browser/network metadata to those websites. The software does not fetch online map tiles or check for updates.

