from decimal import Decimal
from fractions import Fraction
import unittest

from probability_of_us.domain.models import DoubleCountingError, ModelInputError, ProbabilityFactor
from probability_of_us.statistics.probability import (
    as_probability, attempts_for_target, bayes_probability, birthday_collision_probability,
    format_probability, multiply_factors, pair_count, probability_at_least_one,
)


class ProbabilityTests(unittest.TestCase):
    def test_recurrence_known_answer(self):
        self.assertAlmostEqual(probability_at_least_one(Fraction(1, 2), 2), 0.75)
        self.assertAlmostEqual(probability_at_least_one("0.001", 1000), 1 - (1 - 0.001) ** 1000)

    def test_recurrence_edges(self):
        self.assertEqual(probability_at_least_one(0, 100), 0)
        self.assertEqual(probability_at_least_one(0.5, 0), 0)
        self.assertEqual(probability_at_least_one(1, 1), 1)
        self.assertEqual(attempts_for_target(0, Fraction(1, 10)), None)
        self.assertEqual(attempts_for_target(0.5, 0), 0)
        self.assertEqual(attempts_for_target(1, 1), 1)
        self.assertIsNone(attempts_for_target(Fraction(1, 3), 1))
        self.assertEqual(attempts_for_target(0.5, 0.75), 2)

    def test_tiny_probabilities_remain_nonzero(self):
        p = Fraction(1, 10**400)
        result = probability_at_least_one(p, 1)
        self.assertIsInstance(result, Decimal)
        self.assertGreater(result, 0)
        self.assertEqual(format_probability(p), "1.000 × 10^-400")
        needed = attempts_for_target(p, Fraction(1, 2))
        self.assertIsInstance(needed, int)
        self.assertGreater(needed, 10**399)

    def test_probability_validation(self):
        for value in (-0.01, 1.01, float("nan"), float("inf"), "invalid"):
            with self.subTest(value=value), self.assertRaises(ModelInputError):
                as_probability(value)
        for count in (-1, 2.5, True):
            with self.subTest(count=count), self.assertRaises(ModelInputError):
                probability_at_least_one(0.5, count)

    def test_pair_count(self):
        self.assertEqual(pair_count(0), 0)
        self.assertEqual(pair_count(1), 0)
        self.assertEqual(pair_count(5), 10)
        with self.assertRaises(ModelInputError):
            pair_count(-2)

    def test_factor_dependencies_and_double_count(self):
        first = ProbabilityFactor("A", "A", Fraction(1, 2), "n", "1/2", "derived", "test")
        second = ProbabilityFactor("B", "B given A", Fraction(1, 3), "A", "1/3", "assumed", "user", ("A",))
        chain = multiply_factors((first, second))
        self.assertEqual(chain.value, Fraction(1, 6))
        with self.assertRaises(DoubleCountingError):
            multiply_factors((first, first))
        bad = ProbabilityFactor("C", "C given D", Fraction(1, 2), "D", "1/2", "derived", "test", ("D",))
        with self.assertRaises(ModelInputError):
            multiply_factors((bad,))

    def test_incomplete_chain_stays_unknown(self):
        first = ProbabilityFactor("A", "A", Fraction(1, 2), "n", "1/2", "derived", "test")
        second = ProbabilityFactor("B", "B given A", None, "A", "unknown", "unknown", "missing", ("A",))
        self.assertIsNone(multiply_factors((first, second)).value)

    def test_bayes_and_birthday(self):
        self.assertAlmostEqual(bayes_probability(0.01, 0.95, 0.05), 0.16101694915254236)
        self.assertEqual(birthday_collision_probability(1, 365), 0)
        self.assertEqual(birthday_collision_probability(366, 365), 1)


if __name__ == "__main__":
    unittest.main()

