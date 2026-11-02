from fractions import Fraction
import unittest

from probability_of_us.data.default_dataset import default_dataset
from probability_of_us.domain.models import ModelInputError
from probability_of_us.statistics.demography import (
    age_compatibility_probability, age_eligible_pair_count, continent_birth_share,
    country_birth_share, country_within_continent_share, haversine_km,
    hierarchical_country_share, joint_country_probability,
)


class DemographyTests(unittest.TestCase):
    def setUp(self):
        self.data = default_dataset()

    def test_birth_share_uses_birth_counts_and_selected_period(self):
        share = country_birth_share(self.data, "HUN", 2015, 2019)
        self.assertEqual(share, Fraction(202, 942))

    def test_hierarchical_weighting_equals_direct_country_share(self):
        direct = country_birth_share(self.data, "HUN", 2015, 2019)
        hierarchical = hierarchical_country_share(self.data, "HUN", 2015, 2019)
        self.assertEqual(direct, hierarchical)
        europe = continent_birth_share(self.data, "Europe", 2015, 2019)
        within = country_within_continent_share(self.data, "HUN", 2015, 2019)
        self.assertEqual(europe * within, direct)

    def test_pair_probabilities(self):
        self.assertEqual(joint_country_probability(3, 5, 3, 5), Fraction(9, 25))
        self.assertEqual(joint_country_probability(3, 5, 3, 5, same_population_without_replacement=True), Fraction(3, 10))

    def test_age_compatibility_hand_checked(self):
        years = {2000: 2, 2001: 1}
        # Three people: three unique pairs, all within a one-year window.
        self.assertEqual(age_compatibility_probability(years, years, 1, same_population_without_replacement=True), 1)
        self.assertEqual(age_eligible_pair_count(years, 1), 3)
        # Same-year pairs only: one pair out of three.
        self.assertEqual(age_compatibility_probability(years, years, 0, same_population_without_replacement=True), Fraction(1, 3))

    def test_separate_cohorts(self):
        self.assertEqual(age_compatibility_probability({2000: 10}, {2002: 20}, 2), 1)
        self.assertEqual(age_compatibility_probability({2000: 10}, {2002: 20}, 1), 0)

    def test_geodesic_distance(self):
        self.assertEqual(haversine_km(0, 0, 0, 0), 0)
        self.assertAlmostEqual(haversine_km(0, 0, 0, 1), 111.195, delta=0.2)
        with self.assertRaises(ModelInputError):
            haversine_km(91, 0, 0, 0)


if __name__ == "__main__":
    unittest.main()

