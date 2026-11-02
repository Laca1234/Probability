import csv
import json
from pathlib import Path
import tempfile
import unittest

from probability_of_us.data.datasets import load_birth_csv
from probability_of_us.domain.models import ModelInputError
from probability_of_us.security.exports import safe_csv_export, safe_json_export, spreadsheet_safe_cell
from probability_of_us.storage.repository import ScenarioRepository


def workspace_temporary_directory():
    base = Path.cwd() / ".test-tmp"
    base.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base)


class DataStorageSecurityTests(unittest.TestCase):
    def test_csv_import_and_duplicate_rejection(self):
        with workspace_temporary_directory() as temp:
            path = Path(temp) / "births.csv"
            path.write_text("country_code,country_name,continent,year,births\nHUN,Hungary,Europe,2020,3\n", encoding="utf-8")
            dataset = load_birth_csv(path)
            self.assertEqual(dataset.records[0].births, 3)
            path.write_text("country_code,country_name,continent,year,births\nHUN,Hungary,Europe,2020,3\nHUN,Hungary,Europe,2020,4\n", encoding="utf-8")
            with self.assertRaises(ModelInputError):
                load_birth_csv(path)

    def test_rejects_unsafe_or_invalid_input(self):
        with workspace_temporary_directory() as temp:
            path = Path(temp) / "bad.csv"
            path.write_text("country_code,country_name,continent,year,births\nHU,Hungary,Europe,2020,3\n", encoding="utf-8")
            with self.assertRaises(ModelInputError):
                load_birth_csv(path)

    def test_rejects_aggregate_rows_and_incomplete_coverage(self):
        with workspace_temporary_directory() as temp:
            path = Path(temp) / "aggregate.csv"
            path.write_text("country_code,country_name,continent,year,births\nWLD,World,World,2020,100\n", encoding="utf-8")
            with self.assertRaises(ModelInputError):
                load_birth_csv(path)
            path.write_text(
                "country_code,country_name,continent,year,births\n"
                "HUN,Hungary,Europe,2020,5\nHUN,Hungary,Europe,2021,6\n"
                "AUT,Austria,Europe,2020,4\n",
                encoding="utf-8",
            )
            with self.assertRaises(ModelInputError):
                load_birth_csv(path)
            path = Path(temp) / "negative.csv"
            path.write_text("country_code,country_name,continent,year,births\nHUN,Hungary,Europe,2020,-3\n", encoding="utf-8")
            with self.assertRaises(ModelInputError):
                load_birth_csv(path)

    def test_atomic_export_and_formula_neutralization(self):
        self.assertEqual(spreadsheet_safe_cell("=HYPERLINK(\"x\")"), "'=HYPERLINK(\"x\")")
        self.assertEqual(spreadsheet_safe_cell("ordinary"), "ordinary")
        with workspace_temporary_directory() as temp:
            path = Path(temp) / "out.csv"
            safe_csv_export(path, ["name"], [["=1+1"]])
            with path.open(encoding="utf-8-sig", newline="") as file:
                self.assertEqual(next(csv.reader(file))[0], "name")
                self.assertEqual(next(csv.reader(file))[0], "'=1+1")
            json_path = Path(temp) / "manifest.json"
            safe_json_export(json_path, {"x": 1})
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), {"x": 1})

    def test_scenario_repository_round_trip(self):
        with workspace_temporary_directory() as temp:
            repository = ScenarioRepository(Path(temp) / "scenarios.sqlite3")
            scenario_id = repository.save_scenario("Sample", {"country_code": "HUN"}, {"value": "1/2"})
            self.assertEqual(repository.integrity_check(), "ok")
            record = repository.list_scenarios()[0]
            self.assertEqual(record["scenario_id"], scenario_id)
            self.assertEqual(record["inputs"]["country_code"], "HUN")
            self.assertTrue(repository.delete_scenario(scenario_id))
            self.assertFalse(repository.list_scenarios())


if __name__ == "__main__":
    unittest.main()

