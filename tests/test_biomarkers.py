"""
Unit tests for the biomarkers module.
"""

import unittest
import numpy as np
from phenoage_toolkit.biomarkers.calculator import AgeClockCalculator


class TestAgeClockCalculator(unittest.TestCase):
    """Test the AgeClockCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = AgeClockCalculator()
        
        # Sample valid biomarker data
        self.valid_biomarkers = {
            "albumin": 4.5,
            "creatinine": 0.9,
            "glucose": 90,
            "crp": 0.3,
            "lymphocyte": 35,
            "mcv": 90,
            "rdw": 13.0,
            "alkaline_phosphatase": 65,
            "wbc": 5.5,
            "chronological_age": 42
        }
        
        # Sample edge case biomarker data
        self.edge_biomarkers = {
            "albumin": 3.0,          # Low albumin
            "creatinine": 1.5,        # High creatinine
            "glucose": 130,           # High glucose
            "crp": 5.0,               # High CRP
            "lymphocyte": 15,         # Low lymphocyte
            "mcv": 105,               # High MCV
            "rdw": 17.0,              # High RDW
            "alkaline_phosphatase": 150,  # High ALP
            "wbc": 9.5,               # High WBC
            "chronological_age": 60   # Older age
        }
        
    def test_normalize_biomarker_name(self):
        """Test biomarker name normalization."""
        # Test standard names
        self.assertEqual(self.calculator.normalize_biomarker_name("albumin"), "albumin")
        
        # Test aliases
        self.assertEqual(self.calculator.normalize_biomarker_name("alb"), "albumin")
        self.assertEqual(self.calculator.normalize_biomarker_name("creat"), "creatinine")
        self.assertEqual(self.calculator.normalize_biomarker_name("glu"), "glucose")
        self.assertEqual(self.calculator.normalize_biomarker_name("c-reactive protein"), "crp")
        self.assertEqual(self.calculator.normalize_biomarker_name("lymphs"), "lymphocyte")
        self.assertEqual(self.calculator.normalize_biomarker_name("mean cell volume"), "mcv")
        self.assertEqual(self.calculator.normalize_biomarker_name("red cell distribution width"), "rdw")
        self.assertEqual(self.calculator.normalize_biomarker_name("alp"), "alkaline_phosphatase")
        self.assertEqual(self.calculator.normalize_biomarker_name("white blood cells"), "wbc")
        self.assertEqual(self.calculator.normalize_biomarker_name("age"), "chronological_age")
        
        # Test case insensitivity
        self.assertEqual(self.calculator.normalize_biomarker_name("ALBumin"), "albumin")
        self.assertEqual(self.calculator.normalize_biomarker_name("CRP"), "crp")
        
        # Test unknown biomarker
        self.assertEqual(self.calculator.normalize_biomarker_name("unknown_marker"), "unknown_marker")
        
    def test_calculate_phenoage_valid_data(self):
        """Test phenoage calculation with valid data."""
        # Calculate phenoage
        result = self.calculator.calculate_phenoage(self.valid_biomarkers)
        
        # Check that all expected keys are present
        expected_keys = [
            "lin_comb", "mort_score", "pheno_age", "est_dnam_age", "est_d_mscore",
            "terms", "inputs", "converted_inputs"
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that values are in expected ranges
        self.assertGreater(result["pheno_age"], 0)  # Should be positive
        self.assertLess(result["pheno_age"], 100)   # Should be less than 100
        
        self.assertGreaterEqual(result["mort_score"], 0)  # Should be non-negative
        self.assertLessEqual(result["mort_score"], 1)     # Should be at most 1
        
        # Check that est_dnam_age is close to pheno_age (usually slightly lower)
        self.assertLess(result["est_dnam_age"], result["pheno_age"])
        self.assertGreater(result["est_dnam_age"], result["pheno_age"] - 5)
        
    def test_calculate_phenoage_edge_cases(self):
        """Test phenoage calculation with edge case data."""
        # Calculate phenoage
        result = self.calculator.calculate_phenoage(self.edge_biomarkers)
        
        # Edge case should have higher pheno_age than chronological_age
        self.assertGreater(result["pheno_age"], self.edge_biomarkers["chronological_age"])
        
        # Mortality score should be higher than for valid biomarkers
        valid_result = self.calculator.calculate_phenoage(self.valid_biomarkers)
        self.assertGreater(result["mort_score"], valid_result["mort_score"])
        
    def test_calculate_phenoage_missing_biomarkers(self):
        """Test phenoage calculation with missing biomarkers."""
        # Remove a required biomarker
        incomplete_biomarkers = self.valid_biomarkers.copy()
        del incomplete_biomarkers["albumin"]
        
        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.calculator.calculate_phenoage(incomplete_biomarkers)
            
    def test_calculate_phenoage_invalid_values(self):
        """Test phenoage calculation with invalid biomarker values."""
        # Test with negative values
        invalid_biomarkers = self.valid_biomarkers.copy()
        invalid_biomarkers["crp"] = -1  # Negative CRP
        
        # Should not raise an error, but should handle the negative value
        result = self.calculator.calculate_phenoage(invalid_biomarkers)
        self.assertGreaterEqual(result["pheno_age"], 0)
        
    def test_process_direct_input_single(self):
        """Test processing a single set of biomarker data."""
        # Process as single dictionary
        results = self.calculator.process_direct_input(self.valid_biomarkers)
        
        # Should return a list with one item
        self.assertEqual(len(results), 1)
        
        # Should have all original biomarkers plus calculated metrics
        result = results[0]
        for key in self.valid_biomarkers:
            self.assertIn(key, result)
        
        # Should have phenoage metrics
        self.assertIn("phenoage_pheno_age", result)
        self.assertIn("phenoage_mort_score", result)
        
    def test_process_direct_input_multiple(self):
        """Test processing multiple sets of biomarker data."""
        # Create a list of biomarker data
        biomarker_list = [self.valid_biomarkers, self.edge_biomarkers]
        
        # Process as list
        results = self.calculator.process_direct_input(biomarker_list)
        
        # Should return a list with two items
        self.assertEqual(len(results), 2)
        
        # Each item should have phenoage metrics
        for result in results:
            self.assertIn("phenoage_pheno_age", result)
        
    def test_process_direct_input_error_handling(self):
        """Test error handling in process_direct_input."""
        # Create invalid biomarker data
        invalid_biomarkers = {"albumin": 4.5}  # Missing most required biomarkers
        
        # Process it
        results = self.calculator.process_direct_input(invalid_biomarkers)
        
        # Should return a list with one item
        self.assertEqual(len(results), 1)
        
        # Should have an error message
        self.assertIn("error", results[0])
        
    def test_unit_conversions(self):
        """Test that unit conversions are performed correctly."""
        # Calculate phenoage to get converted values
        result = self.calculator.calculate_phenoage(self.valid_biomarkers)
        
        # Check specific unit conversions
        self.assertAlmostEqual(
            result["converted_inputs"]["albumin"],
            self.valid_biomarkers["albumin"] * 10,  # g/dL to g/L
            places=4
        )
        
        self.assertAlmostEqual(
            result["converted_inputs"]["creatinine"],
            self.valid_biomarkers["creatinine"] * 88.4,  # mg/dL to μmol/L
            places=4
        )
        
        self.assertAlmostEqual(
            result["converted_inputs"]["glucose"],
            self.valid_biomarkers["glucose"] * 0.0555,  # mg/dL to mmol/L
            places=4
        )
        
        # CRP has special handling (log transformation)
        self.assertIsNotNone(result["converted_inputs"]["crp"])
        
    def test_extremely_low_crp(self):
        """Test handling of extremely low CRP values that might cause log(0) issues."""
        # Create biomarker data with zero CRP
        zero_crp_biomarkers = self.valid_biomarkers.copy()
        zero_crp_biomarkers["crp"] = 0
        
        # Should not raise an error
        try:
            result = self.calculator.calculate_phenoage(zero_crp_biomarkers)
            self.assertIsNotNone(result)
            self.assertGreater(result["pheno_age"], 0)
        except Exception as e:
            self.fail(f"calculate_phenoage raised {type(e).__name__} unexpectedly!")


if __name__ == "__main__":
    unittest.main()
