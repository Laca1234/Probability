from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from probability_of_us.application.app_controller import AppController
from probability_of_us.storage.repository import ScenarioRepository


def workspace_temporary_directory():
    base = Path.cwd() / ".test-tmp"
    base.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = workspace_temporary_directory()
        self.database = Path(self.temp.name) / "app.sqlite3"
        self.controller = AppController(ScenarioRepository(self.database))

    def tearDown(self):
        del self.controller
        self.temp.cleanup()

    def test_analysis_surfaces_known_and_unknown_factors(self):
        result = self.controller.analyzeStory("HUN", 2015, 2019, 3, "", "", "Not specified")
        self.assertTrue(result["ok"])
        self.assertNotEqual(result["demographicProbability"], "0/1")
        self.assertIsNone(result["fullProbability"])
        self.assertEqual(result["factors"][2]["evidence"], "unknown")
        self.assertTrue(result["manifestId"])

    def test_assumptions_are_marked_and_scenario_can_be_saved(self):
        result = self.controller.analyzeStory("HUN", 2015, 2019, 3, "0.01", "0.1", "Dating app")
        self.assertTrue(result["ok"])
        self.assertEqual(result["factors"][2]["evidence"], "assumed")
        self.assertEqual(result["factors"][3]["evidence"], "assumed")
        self.assertTrue(self.controller.saveCurrentScenario("Test scenario"))
        self.assertEqual(self.controller.savedScenarios[0]["name"], "Test scenario")

    def test_recurrence_ui_boundary_preserves_decimal_targets(self):
        result = self.controller.calculateRecurrence("0.001", 1000, 99.9)
        self.assertTrue(result["ok"])
        self.assertEqual(result["target"], 99.9)
        self.assertGreater(result["needed"], 1)

    def test_imported_dataset_and_provenance_survive_restart(self):
        csv_path = Path(self.temp.name) / "births.csv"
        csv_path.write_text(
            "country_code,country_name,continent,year,births\n"
            "HUN,Hungary,Europe,2020,5\nAUT,Austria,Europe,2020,4\n"
            "HUN,Hungary,Europe,2021,6\nAUT,Austria,Europe,2021,5\n",
            encoding="utf-8",
        )
        local_data = Path(self.temp.name) / "local"
        with patch.dict(os.environ, {"LOCALAPPDATA": str(local_data)}):
            self.assertTrue(self.controller.importBirthCsv(
                str(csv_path), "Test births", "Test publisher", "https://example.test/data",
                "Open test license", "derived",
            ))
            digest = self.controller.datasetSha256
            del self.controller
            reopened = AppController(ScenarioRepository(self.database))
            self.controller = reopened
            self.assertEqual(reopened.datasetName, "Test births")
            self.assertEqual(reopened.datasetSha256, digest)
            self.assertEqual(reopened.datasetPublisher, "Test publisher")
            self.assertEqual(reopened.datasetSource, "https://example.test/data")
            self.assertEqual(reopened.datasetKind, "derived")


if __name__ == "__main__":
    unittest.main()

