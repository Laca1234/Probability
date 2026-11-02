"""Qt bridge: validates user input and orchestrates independent model services."""

from __future__ import annotations

import json
import platform
import threading
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QLabel, QLineEdit, QVBoxLayout,
)

from probability_of_us import MODEL_VERSION, __version__
from probability_of_us.data.datasets import load_birth_csv, validate_dataset_totals
from probability_of_us.data.default_dataset import default_dataset
from probability_of_us.domain.models import (
    BirthDataset, DatasetProvenance, Scenario, ScenarioResult, ModelInputError,
)
from probability_of_us.security.exports import safe_csv_export, safe_json_export, safe_markdown_export
from probability_of_us.statistics.demography import selected_rows
from probability_of_us.statistics.probability import (
    as_probability, attempts_for_target, bayes_probability, birthday_collision_probability,
    format_probability, pair_count, probability_at_least_one, probability_odds,
)
from probability_of_us.statistics.story_model import analyze_story
from probability_of_us.statistics.simulation import simulate_bernoulli
from probability_of_us.storage.repository import ScenarioRepository, default_database_path


def _fraction_text(value: Fraction | None) -> str | None:
    return None if value is None else f"{value.numerator}/{value.denominator}"


def _fraction_from_text(value: str | None) -> Fraction | None:
    return None if not value else Fraction(value)


class _WorkerSignals(QObject):
    progress = Signal(int, int)
    finished = Signal(object)
    failed = Signal(str)


class _SimulationWorker(QRunnable):
    def __init__(self, p: float, trials: int, seed: int, cancel_event: threading.Event):
        super().__init__()
        self.signals = _WorkerSignals()
        self.p, self.trials, self.seed, self.cancel_event = p, trials, seed, cancel_event

    @Slot()
    def run(self) -> None:
        try:
            result = simulate_bernoulli(
                self.p, self.trials, self.seed,
                cancelled=self.cancel_event.is_set,
                progress=lambda done, total: self.signals.progress.emit(done, total),
            )
            self.signals.finished.emit(result)
        except InterruptedError:
            self.signals.failed.emit("Simulation cancelled.")
        except Exception as exc:  # user-visible error boundary
            self.signals.failed.emit(str(exc))


class AppController(QObject):
    changed = Signal()
    simulationProgress = Signal(int, int)
    simulationFinished = Signal(object)
    simulationError = Signal(str)

    def __init__(self, repository: ScenarioRepository | None = None):
        super().__init__()
        self._repository = repository or ScenarioRepository(default_database_path())
        self._dataset: BirthDataset = default_dataset()
        self._status = "Ready · offline"
        self._restore_active_dataset()
        self._dark_theme = bool(self._repository.get_preference("dark_theme", True))
        self._last_result: ScenarioResult | None = None
        self._last_manifest: dict[str, Any] | None = None
        self._last_inputs: dict[str, Any] | None = None
        self._recent_calculation_ms: float | None = None
        self._simulation_cancel = threading.Event()
        self._worker: _SimulationWorker | None = None
        self._thread_pool = QThreadPool.globalInstance()

    @Property(str, notify=changed)
    def appVersion(self) -> str:
        return __version__

    @Property(str, notify=changed)
    def modelVersion(self) -> str:
        return MODEL_VERSION

    @Property(str, notify=changed)
    def datasetName(self) -> str:
        return self._dataset.provenance.name

    @Property(str, notify=changed)
    def datasetSummary(self) -> str:
        years = self._dataset.years
        return f"{self._dataset.provenance.kind.title()} · {years[0]}–{years[-1]} · {len(self._dataset.records)} country-year rows"

    @Property(str, notify=changed)
    def datasetSha256(self) -> str:
        return self._dataset.provenance.sha256

    @Property(str, notify=changed)
    def datasetPublisher(self) -> str:
        return self._dataset.provenance.publisher

    @Property(str, notify=changed)
    def datasetSource(self) -> str:
        return self._dataset.provenance.source_url

    @Property(str, notify=changed)
    def datasetLicense(self) -> str:
        return self._dataset.provenance.license

    @Property(str, notify=changed)
    def datasetKind(self) -> str:
        return self._dataset.provenance.kind

    @Property(str, notify=changed)
    def datasetAccessedOn(self) -> str:
        return self._dataset.provenance.accessed_on

    @Property(list, notify=changed)
    def datasetWarnings(self) -> list[str]:
        return list(validate_dataset_totals(self._dataset))

    @Property(str, notify=changed)
    def statusText(self) -> str:
        return self._status

    @Property(bool, notify=changed)
    def darkTheme(self) -> bool:
        return self._dark_theme

    @Property(str, notify=changed)
    def lastCalculation(self) -> str:
        if self._recent_calculation_ms is None:
            return "No calculation yet"
        return f"Last calculation · {self._recent_calculation_ms:.1f} ms"

    @Property(list, notify=changed)
    def countryOptions(self) -> list[dict[str, str]]:
        return [{"code": code, "name": name} for code, name in self._dataset.countries]

    @Property(list, notify=changed)
    def countryShares(self) -> list[dict[str, Any]]:
        first, last = self._dataset.years[0], self._dataset.years[-1]
        rows = selected_rows(self._dataset, first, last)
        total = sum(row.births for row in rows)
        country_totals: dict[str, dict[str, Any]] = {}
        for row in rows:
            item = country_totals.setdefault(row.country_code, {"code": row.country_code, "name": row.country_name, "births": 0, "continent": row.continent})
            item["births"] += row.births
        result = []
        for item in country_totals.values():
            item["share"] = item["births"] / total if total else 0
            result.append(item)
        return sorted(result, key=lambda item: item["births"], reverse=True)

    @Property(list, notify=changed)
    def savedScenarios(self) -> list[dict[str, Any]]:
        saved = self._repository.list_scenarios()
        return [{"scenario_id": item["scenario_id"], "name": item["name"],
                 "updated_at": item["updated_at"],
                 "probability": item["result"].get("demographic_probability_display", "Unknown"),
                 "country_code": item["inputs"].get("country_code", "")}
                for item in saved]

    @Slot()
    def toggleTheme(self) -> None:
        self._dark_theme = not self._dark_theme
        self._repository.set_preference("dark_theme", self._dark_theme)
        self._status = "Dark theme enabled" if self._dark_theme else "Light theme enabled"
        self.changed.emit()

    @Slot(str)
    def setStatus(self, message: str) -> None:
        self._status = message[:180]
        self.changed.emit()

    @Slot(str, int, int, int, str, str, str, result="QVariantMap")
    def analyzeStory(self, country_code: str, start_year: int, end_year: int, max_gap: int,
                     meeting_text: str, relationship_text: str, meeting_channel: str) -> dict[str, Any]:
        import time
        start = time.perf_counter()
        try:
            target_code = country_code.strip().upper()
            meeting = as_probability(meeting_text.strip()) if meeting_text.strip() else None
            relationship = as_probability(relationship_text.strip()) if relationship_text.strip() else None
            scenario = Scenario(
                name=f"{target_code} · {start_year}–{end_year}",
                country_code=target_code,
                start_year=start_year,
                end_year=end_year,
                max_birth_year_gap=max_gap,
                meeting_probability=meeting,
                relationship_probability=relationship,
                meeting_channel=meeting_channel,
                dataset_id=self._dataset.provenance.dataset_id,
            )
            result = analyze_story(self._dataset, scenario)
            chain = result.chain
            world_total = result.population_size
            country_total = result.target_country_births
            eligible_pairs = result.eligible_country_pairs
            denominator_pairs = result.all_population_pairs
            demography = result.demographic_probability
            factors = chain.factors
            self._last_result = result
            self._last_inputs = {
                "country_code": target_code, "start_year": start_year, "end_year": end_year,
                "max_birth_year_gap": max_gap, "meeting_probability": _fraction_text(meeting),
                "relationship_probability": _fraction_text(relationship), "meeting_channel": meeting_channel,
            }
            self._last_manifest = self._build_manifest(result)
            self._recent_calculation_ms = (time.perf_counter() - start) * 1000
            warnings = list(chain.warnings)
            if self._dataset.provenance.kind == "synthetic":
                warnings.insert(0, "Synthetic teaching data only: this result is not an estimate about the real world.")
            if self._dataset.provenance.kind == "unknown":
                warnings.insert(0, "Imported data source status is unknown; verify its source, definitions, and license.")
            if country_total < 2:
                warnings.insert(0, "Fewer than two target-country births exist in this cohort; the conditional age factor is set to zero.")
            self._status = "Analysis calculated · assumptions are visible below"
            self.changed.emit()
            return {
                "ok": True,
                "demographicProbability": _fraction_text(demography),
                "demographicDisplay": format_probability(demography),
                "demographicOdds": probability_odds(demography),
                "fullProbability": _fraction_text(chain.value),
                "fullDisplay": format_probability(chain.value),
                "fullOdds": probability_odds(chain.value),
                "population": f"{world_total:,} represented births · {denominator_pairs:,} unordered pairs",
                "targetBirths": country_total,
                "eligiblePairs": eligible_pairs,
                "resultScope": result.result_scope,
                "datasetName": self._dataset.provenance.name,
                "datasetKind": self._dataset.provenance.kind,
                "datasetHash": self._dataset.provenance.sha256,
                "factors": [{"label": f.label, "probability": _fraction_text(f.probability),
                             "display": format_probability(f.probability), "denominator": f.denominator,
                             "formula": f.formula, "evidence": f.evidence, "source": f.source}
                            for f in factors],
                "warnings": warnings,
                "manifestId": self._last_manifest["manifest_id"],
            }
        except Exception as exc:
            self._status = f"Could not calculate · {str(exc)[:140]}"
            self.changed.emit()
            return {"ok": False, "error": str(exc)}

    def _build_manifest(self, result: ScenarioResult) -> dict[str, Any]:
        import hashlib
        import numpy
        payload = {
            "model_version": MODEL_VERSION,
            "application_version": __version__,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "inputs": self._last_inputs or {},
            "dataset": {
                "dataset_id": self._dataset.provenance.dataset_id,
                "name": self._dataset.provenance.name,
                "version": self._dataset.provenance.version,
                "kind": self._dataset.provenance.kind,
                "sha256": self._dataset.provenance.sha256,
                "source_url": self._dataset.provenance.source_url,
                "publisher": self._dataset.provenance.publisher,
                "accessed_on": self._dataset.provenance.accessed_on,
                "reference_period": self._dataset.provenance.reference_period,
                "license": self._dataset.provenance.license,
                "limitations": list(self._dataset.provenance.limitations),
            },
            "method": "exact integer pair counts and Fraction arithmetic; distinct unordered pairs; no simulation",
            "factors": [{"event_id": item.event_id, "conditional_probability": _fraction_text(item.probability),
                         "evidence": item.evidence, "source": item.source, "formula": item.formula,
                         "denominator": item.denominator, "conditioned_on": list(item.conditioned_on),
                         "assumption_id": item.assumption_id} for item in result.chain.factors],
            "demographic_probability": result.metadata["demographic_probability"],
            "complete_story_probability": _fraction_text(result.chain.value),
            "software": {"python": platform.python_version(), "platform": platform.platform(),
                         "PySide6": __import__("PySide6").__version__, "NumPy": numpy.__version__},
            "random_seed": None,
            "simulation_budget": None,
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        payload["manifest_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
        return payload

    @Slot(str, int, float, result="QVariantMap")
    def calculateRecurrence(self, probability_text: str, attempts: int, target_percent: float) -> dict[str, Any]:
        try:
            p = as_probability(probability_text.strip())
            if not 0 <= target_percent <= 100:
                raise ModelInputError("Target must be between 0% and 100%.")
            target = Fraction(str(target_percent)) / 100
            reached = probability_at_least_one(p, attempts)
            needed = attempts_for_target(p, target)
            self._status = "Recurrence calculated · independent attempts assumed"
            self.changed.emit()
            return {"ok": True, "p": _fraction_text(p), "attempts": attempts,
                    "reachedPercent": format_probability(reached * 100) + "%",
                    "target": target_percent, "needed": needed,
                    "neededText": f"{needed:,}" if needed is not None else ("0" if target_percent == 0 else "Unreachable / infinite"),
                    "warning": "Assumes independent attempts with constant probability. Births and overlapping pairs are not automatically attempts."}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    @Slot(int, result=str)
    def calculatePairs(self, n: int) -> str:
        try:
            return f"{pair_count(n):,} unique unordered pairs · pair opportunities may overlap and are not independent attempts."
        except Exception as exc:
            return str(exc)

    @Slot(str, str, str, result=str)
    def calculateBayes(self, prior: str, sensitivity: str, false_positive: str) -> str:
        try:
            result = bayes_probability(float(prior), float(sensitivity), float(false_positive))
            return f"P(H | +) = {result:.6g} ({result * 100:.4g}%)"
        except Exception as exc:
            return str(exc)

    @Slot(int, int, result=str)
    def calculateBirthday(self, people: int, categories: int) -> str:
        try:
            result = birthday_collision_probability(people, categories)
            return f"{result:.6g} ({result * 100:.4g}%)"
        except Exception as exc:
            return str(exc)

    @Slot(str, int, int)
    def startSimulation(self, probability_text: str, trials: int, seed: int) -> None:
        try:
            probability = float(as_probability(probability_text.strip()))
            if trials > 50_000_000:
                raise ModelInputError("Simulation budget is capped at 50 million trials.")
            self._simulation_cancel.clear()
            worker = _SimulationWorker(probability, trials, seed, self._simulation_cancel)
            worker.signals.progress.connect(self.simulationProgress.emit)
            worker.signals.finished.connect(self._on_simulation_finished)
            worker.signals.failed.connect(self._on_simulation_error)
            self._worker = worker
            self._thread_pool.start(worker)
            self._status = "Simulation running locally · no data is transmitted"
            self.changed.emit()
        except Exception as exc:
            self._on_simulation_error(str(exc))

    @Slot()
    def cancelSimulation(self) -> None:
        self._simulation_cancel.set()

    @Slot(object)
    def _on_simulation_finished(self, result: Any) -> None:
        self.simulationFinished.emit({"probability": result.probability, "trials": result.trials,
            "successes": result.successes, "seed": result.seed, "lower": result.lower_95,
            "upper": result.upper_95, "method": result.method, "note": result.zero_success_note})
        self._worker = None
        self._status = "Simulation complete"
        self.changed.emit()

    @Slot(str)
    def _on_simulation_error(self, message: str) -> None:
        self.simulationError.emit(message)
        self._worker = None
        self._status = message
        self.changed.emit()

    @Slot(str, result=bool)
    def saveCurrentScenario(self, name: str) -> bool:
        if self._last_result is None or self._last_manifest is None or self._last_inputs is None:
            self._status = "Calculate a story before saving it"
            self.changed.emit()
            return False
        try:
            summary = {
                "demographic_probability": _fraction_text(self._last_result.demographic_probability),
                "demographic_probability_display": format_probability(self._last_result.demographic_probability),
                "complete_story_probability": _fraction_text(self._last_result.chain.value),
                "manifest_id": self._last_manifest["manifest_id"],
            }
            self._repository.save_scenario(name, self._last_inputs, {**summary, "manifest": self._last_manifest})
            self._status = "Scenario saved locally"
            self.changed.emit()
            return True
        except Exception as exc:
            self._status = f"Could not save scenario · {exc}"
            self.changed.emit()
            return False

    @Slot(str, result=bool)
    def deleteScenario(self, scenario_id: str) -> bool:
        deleted = self._repository.delete_scenario(scenario_id)
        self._status = "Scenario deleted" if deleted else "Scenario not found"
        self.changed.emit()
        return deleted

    @Slot(str, result="QVariantMap")
    def restoreScenario(self, scenario_id: str) -> dict[str, Any]:
        for item in self._repository.list_scenarios():
            if item["scenario_id"] == scenario_id:
                self._status = f"Loaded saved scenario · {item['name']}"
                self.changed.emit()
                return item["inputs"]
        return {}

    def _restore_active_dataset(self) -> None:
        metadata = self._repository.get_preference("active_dataset", None)
        if not isinstance(metadata, dict):
            return
        try:
            local_path = Path(metadata["path"])
            dataset = load_birth_csv(
                local_path,
                dataset_id=str(metadata["dataset_id"]),
                dataset_name=str(metadata["name"]),
                publisher=str(metadata["publisher"]),
                source_url=str(metadata["source_url"]),
                license_text=str(metadata["license"]),
                version=str(metadata["version"]),
                kind=str(metadata.get("kind", "unknown")),
            )
            if dataset.provenance.sha256 != metadata["sha256"]:
                raise ModelInputError("Stored dataset hash does not match the imported file.")
            p = dataset.provenance
            self._dataset = BirthDataset(dataset.records, DatasetProvenance(
                dataset_id=p.dataset_id, name=p.name, publisher=p.publisher, source_url=p.source_url,
                accessed_on=str(metadata.get("accessed_on", p.accessed_on)), reference_period=p.reference_period,
                license=p.license, version=p.version, sha256=p.sha256, kind=p.kind, limitations=p.limitations,
            ))
        except Exception as exc:
            self._status = f"Saved dataset unavailable; using teaching data · {str(exc)[:100]}"

    @Slot(str, str, str, str, str, str, result=bool)
    def importBirthCsv(self, path: str, dataset_name: str, publisher: str, source_url: str, license_text: str, kind: str) -> bool:
        try:
            dataset = load_birth_csv(
                path, dataset_name=dataset_name.strip() or Path(path).stem,
                publisher=publisher, source_url=source_url, license_text=license_text, kind=kind,
            )
            warnings = validate_dataset_totals(dataset)
            # Keep a validated, immutable-by-hash copy under the user's local application data.
            import os
            from probability_of_us.security.exports import _atomic_write
            local_root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ProbabilityOfUs" / "datasets"
            local_root.mkdir(parents=True, exist_ok=True)
            stored_path = local_root / f"{dataset.provenance.sha256}.csv"
            _atomic_write(stored_path, Path(path).read_bytes())
            self._dataset = load_birth_csv(stored_path,
                dataset_id=dataset.provenance.dataset_id,
                dataset_name=dataset.provenance.name,
                publisher=dataset.provenance.publisher,
                source_url=dataset.provenance.source_url,
                license_text=dataset.provenance.license,
                version=dataset.provenance.version, kind=dataset.provenance.kind)
            self._repository.set_preference("active_dataset", {
                "path": str(stored_path), "dataset_id": self._dataset.provenance.dataset_id,
                "name": self._dataset.provenance.name, "publisher": self._dataset.provenance.publisher,
                "source_url": self._dataset.provenance.source_url, "license": self._dataset.provenance.license,
                "version": self._dataset.provenance.version, "sha256": self._dataset.provenance.sha256,
                "kind": self._dataset.provenance.kind, "accessed_on": self._dataset.provenance.accessed_on,
            })
            self._status = f"Imported and validated dataset · {len(self._dataset.records)} records · {len(warnings)} quality notes"
            self._last_result = None
            self.changed.emit()
            return True
        except Exception as exc:
            self._status = f"Import failed · {str(exc)[:120]}"
            self.changed.emit()
            return False

    @Slot()
    def chooseAndImportDataset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(None, "Import birth-count CSV", "", "CSV files (*.csv)")
        if path:
            dialog = QDialog()
            dialog.setWindowTitle("Dataset provenance")
            dialog.setMinimumWidth(520)
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Record the source and redistribution terms. Leave a field as Not supplied when unknown."))
            form = QFormLayout()
            name_field = QLineEdit(Path(path).stem)
            publisher_field = QLineEdit("Not supplied")
            source_field = QLineEdit("Not supplied")
            license_field = QLineEdit("Not supplied; verify before redistribution")
            kind_field = QComboBox()
            kind_field.addItem("Unknown / not classified", "unknown")
            kind_field.addItem("Original data", "original")
            kind_field.addItem("Derived / transformed", "derived")
            kind_field.addItem("Estimate or projection", "estimated")
            form.addRow("Dataset name", name_field)
            form.addRow("Publisher", publisher_field)
            form.addRow("Source URL", source_field)
            form.addRow("License / redistribution terms", license_field)
            form.addRow("Source-data status", kind_field)
            layout.addLayout(form)
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.importBirthCsv(path, name_field.text(), publisher_field.text(), source_field.text(), license_field.text(), str(kind_field.currentData()))

    @Slot(str)
    def exportCurrent(self, kind: str) -> None:
        if self._last_manifest is None or self._last_result is None:
            self._status = "Calculate a story before exporting"
            self.changed.emit()
            return
        extensions = {"json": ("JSON manifest (*.json)", ".json"), "markdown": ("Markdown report (*.md)", ".md"), "csv": ("CSV factors (*.csv)", ".csv")}
        if kind not in extensions:
            return
        filter_text, suffix = extensions[kind]
        path, _ = QFileDialog.getSaveFileName(None, "Export calculation", f"probability-of-us-report{suffix}", filter_text)
        if not path:
            return
        try:
            if kind == "json":
                safe_json_export(path, self._last_manifest)
            elif kind == "markdown":
                safe_markdown_export(path, self._markdown_report())
            else:
                headers = ["event", "conditional_probability", "evidence", "denominator", "formula", "source"]
                rows = [[f.event_id, _fraction_text(f.probability) or "unknown", f.evidence, f.denominator, f.formula, f.source]
                        for f in self._last_result.chain.factors]
                safe_csv_export(path, headers, rows)
            self._status = f"Exported report · {Path(path).name}"
        except Exception as exc:
            self._status = f"Export failed · {str(exc)[:120]}"
        self.changed.emit()

    def _markdown_report(self) -> str:
        assert self._last_result is not None and self._last_manifest is not None
        lines = ["# Probability of Us · illustrative analysis", "",
                 f"- Model: `{MODEL_VERSION}`", f"- Dataset: {self._dataset.provenance.name} (`{self._dataset.provenance.version}`)",
                 f"- Dataset SHA-256: `{self._dataset.provenance.sha256}`", f"- Manifest ID: `{self._last_manifest['manifest_id']}`", "",
                 "## Scenario", "",
                 f"- Target birthplace: `{self._last_result.scenario.country_code}`",
                 f"- Birth-year range: {self._last_result.scenario.start_year}–{self._last_result.scenario.end_year}",
                 f"- Maximum birth-year difference: {self._last_result.scenario.max_birth_year_gap}",
                 f"- Meeting channel: {self._last_result.scenario.meeting_channel}",
                 f"- Meeting probability assumption: `{_fraction_text(self._last_result.scenario.meeting_probability) or 'unknown'}`",
                 f"- Relationship probability assumption: `{_fraction_text(self._last_result.scenario.relationship_probability) or 'unknown'}`", "",
                 "## Population and denominator", "", self._last_result.result_scope,
                 f"Cohort size represented in this dataset: {self._last_result.population_size:,} births.",
                 f"Target-country births: {self._last_result.target_country_births:,}.", "",
                 "## Conditional factors", ""]
        for factor in self._last_result.chain.factors:
            lines.extend([f"### {factor.label}", "", f"- Value: `{_fraction_text(factor.probability) or 'unknown'}` ({format_probability(factor.probability)})",
                          f"- Formula: `{factor.formula}`", f"- Denominator: {factor.denominator}",
                          f"- Evidence: {factor.evidence}; {factor.source}", ""])
        lines.extend(["## Caveats", "", "Birthplace is not nationality or current residence. Meeting and relationship probabilities are unknown unless entered as explicit user assumptions.",
                      "The bundled teaching dataset is synthetic and must not be interpreted as real demographic data.",
                      "A recurrence calculation requires independent, constant-probability attempts; pairs sharing people are dependent.", ""])
        return "\n".join(lines)

