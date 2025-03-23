"""
Unit tests for the percentile module.
"""

import unittest
import numpy as np
from scipy.stats import norm
from phenoage_toolkit.percentile.calculator import (
    calculate_percentile, 
    get_reference_values, 
    interpret_percentile, 
    STD_DEV
)


class TestPercentileCalculator(unittest.TestCase):
    """Test the percentile calculator functions."""
    
    def test_calculate_percentile_younger(self):
        """Test percentile calculation when phenotypic age is younger."""
        # When phenotypic age is younger than chronological age
        chronological_age = 50
        phenotypic_age = 45  # 5 years younger
        
        percentile = calculate_percentile(chronological_age, phenotypic_age)
        
        # Should be better than 50th percentile
        self.assertGreater(percentile, 50)
        
        # Calculate expected percentile manually
        z_score = (phenotypic_age - chronological_age) / STD_DEV
        expected_percentile = (1 - norm.cdf(z_score)) * 100
        
        # Should match expected value
        self.assertAlmostEqual(percentile, expected_percentile, places=4)
        
    def test_calculate_percentile_older(self):
        """Test percentile calculation when phenotypic age is older."""
        # When phenotypic age is older than chronological age
        chronological_age = 50
        phenotypic_age = 55  # 5 years older
        
        percentile = calculate_percentile(chronological_age, phenotypic_age)
        
        # Should be worse than 50th percentile
        self.assertLess(percentile, 50)
        
        # Calculate expected percentile manually
        z_score = (phenotypic_age - chronological_age) / STD_DEV
        expected_percentile = (1 - norm.cdf(z_score)) * 100
        
        # Should match expected value
        self.assertAlmostEqual(percentile, expected_percentile, places=4)
        
    def test_calculate_percentile_equal(self):
        """Test percentile calculation when phenotypic age equals chronological age."""
        # When phenotypic age equals chronological age
        chronological_age = 50
        phenotypic_age = 50  # Same age
        
        percentile = calculate_percentile(chronological_age, phenotypic_age)
        
        # Should be exactly 50th percentile
        self.assertAlmostEqual(percentile, 50, places=4)
        
    def test_calculate_percentile_extreme_young(self):
        """Test percentile calculation with extremely young phenotypic age."""
        # When phenotypic age is extremely young
        chronological_age = 50
        phenotypic_age = 30  # 20 years younger
        
        percentile = calculate_percentile(chronological_age, phenotypic_age)
        
        # Should be very high percentile
        self.assertGreater(percentile, 99)
        
    def test_calculate_percentile_extreme_old(self):
        """Test percentile calculation with extremely old phenotypic age."""
        # When phenotypic age is extremely old
        chronological_age = 50
        phenotypic_age = 70  # 20 years older
        
        percentile = calculate_percentile(chronological_age, phenotypic_age)
        
        # Should be very low percentile
        self.assertLess(percentile, 1)
        
    def test_get_reference_values(self):
        """Test reference values generation."""
        # Get reference values for age 50
        references = get_reference_values(50)
        
        # Should have all expected percentiles
        expected_percentiles = ['10th', '25th', '50th', '75th', '90th']
        for percentile in expected_percentiles:
            self.assertIn(percentile, references)
            
        # 50th percentile should equal chronological age
        self.assertEqual(references['50th'], 50)
        
        # Lower percentiles should have higher phenotypic ages
        self.assertGreater(references['10th'], references['25th'])
        self.assertGreater(references['25th'], references['50th'])
        
        # Higher percentiles should have lower phenotypic ages
        self.assertLess(references['75th'], references['50th'])
        self.assertLess(references['90th'], references['75th'])
        
        # The differences between adjacent percentiles should be roughly equal
        diff_10_25 = references['10th'] - references['25th']
        diff_25_50 = references['25th'] - references['50th']
        diff_50_75 = references['50th'] - references['75th']
        diff_75_90 = references['75th'] - references['90th']
        
        self.assertAlmostEqual(diff_10_25, diff_25_50, delta=0.1)
        self.assertAlmostEqual(diff_25_50, diff_50_75, delta=0.1)
        self.assertAlmostEqual(diff_50_75, diff_75_90, delta=0.1)
        
    def test_interpret_percentile(self):
        """Test percentile interpretation."""
        # Test excellent range
        interpretation_90 = interpret_percentile(90)
        interpretation_95 = interpret_percentile(95)
        self.assertEqual(
            interpretation_90,
            "Excellent - younger biological age than 90% of people your age"
        )
        self.assertEqual(interpretation_90, interpretation_95)  # Same interpretation
        
        # Test very good range
        interpretation_75 = interpret_percentile(75)
        interpretation_85 = interpret_percentile(85)
        self.assertEqual(
            interpretation_75,
            "Very good - younger biological age than 75% of people your age"
        )
        self.assertEqual(interpretation_75, interpretation_85)  # Same interpretation
        
        # Test good range
        interpretation_50 = interpret_percentile(50)
        interpretation_60 = interpret_percentile(60)
        self.assertEqual(
            interpretation_50,
            "Good - younger biological age than average"
        )
        self.assertEqual(interpretation_50, interpretation_60)  # Same interpretation
        
        # Test below average range
        interpretation_25 = interpret_percentile(25)
        interpretation_30 = interpret_percentile(30)
        self.assertEqual(
            interpretation_25,
            "Below average - older biological age than average"
        )
        self.assertEqual(interpretation_25, interpretation_30)  # Same interpretation
        
        # Test poor range
        interpretation_10 = interpret_percentile(10)
        interpretation_15 = interpret_percentile(15)
        self.assertEqual(
            interpretation_10,
            "Poor - older biological age than 75% of people your age"
        )
        self.assertEqual(interpretation_10, interpretation_15)  # Same interpretation
        
        # Test concerning range
        interpretation_5 = interpret_percentile(5)
        self.assertEqual(
            interpretation_5,
            "Concerning - older biological age than 90% of people your age"
        )
        
    def test_std_dev_value(self):
        """Test that STD_DEV has the expected value."""
        self.assertEqual(STD_DEV, 5.5)


if __name__ == "__main__":
    unittest.main()
