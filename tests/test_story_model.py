import unittest
from fractions import Fraction

from probability_of_us.data.default_dataset import default_dataset
from probability_of_us.domain.models import Scenario
from probability_of_us.statistics.story_model import analyze_story


class StoryModelTests(unittest.TestCase):
    def test_unknown_meeting_and_relationship_are_not_invented(self):
        result = analyze_story(default_dataset(), Scenario("Demo", "HUN", 2015, 2019, 3))
        self.assertIsNone(result.chain.value)
        self.assertIsNotNone(result.chain.factors[0].probability)
        self.assertIsNotNone(result.chain.factors[1].probability)
        self.assertIsNone(result.chain.factors[2].probability)
        self.assertIn("demographic_probability", result.metadata)

    def test_explicit_assumptions_are_multiplicative_and_labelled(self):
        result = analyze_story(default_dataset(), Scenario(
            "Illustrative", "HUN", 2015, 2019, 3,
            meeting_probability=Fraction(1, 100), relationship_probability=Fraction(1, 10),
        ))
        demographic = Fraction(result.metadata["demographic_probability"])
        self.assertEqual(result.chain.value, demographic * Fraction(1, 1000))
        self.assertEqual(result.chain.factors[2].evidence, "assumed")
        self.assertEqual(result.chain.factors[3].evidence, "assumed")

    def test_pair_count_matches_joint_decomposition(self):
        result = analyze_story(default_dataset(), Scenario("Demo", "HUN", 2015, 2019, 3))
        direct = Fraction(result.eligible_country_pairs, result.all_population_pairs)
        self.assertEqual(direct, Fraction(result.metadata["demographic_probability"]))


if __name__ == "__main__":
    unittest.main()

