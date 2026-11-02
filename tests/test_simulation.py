import unittest

from probability_of_us.domain.models import ModelInputError
from probability_of_us.statistics.simulation import simulate_bernoulli


class SimulationTests(unittest.TestCase):
    def test_seed_reproduces_result(self):
        first = simulate_bernoulli(0.2, 10000, 42)
        second = simulate_bernoulli(0.2, 10000, 42)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first.probability, 0.2)
        self.assertLessEqual(first.lower_95, first.upper_95)

    def test_zero_success_is_not_impossibility(self):
        result = simulate_bernoulli(1e-9, 100, 42)
        self.assertEqual(result.successes, 0)
        self.assertGreater(result.upper_95, 0)
        self.assertIn("not proof of impossibility", result.zero_success_note)

    def test_budget_and_seed_validation(self):
        with self.assertRaises(ModelInputError):
            simulate_bernoulli(0.5, 0, 1)
        with self.assertRaises(ModelInputError):
            simulate_bernoulli(0.5, 1, -1)


if __name__ == "__main__":
    unittest.main()

