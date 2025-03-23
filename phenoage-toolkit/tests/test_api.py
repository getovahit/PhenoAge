"""
Unit tests for the PhenoAge API.
"""

import unittest
from phenoage_toolkit.api import PhenoAgeAPI


class TestPhenoAgeAPI(unittest.TestCase):
    """Test the PhenoAgeAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = PhenoAgeAPI()
        
        # Sample biomarker data
        self.biomarker_data = {
            "albumin": 4.2,
            "creatinine": 0.9,
            "glucose": 90,
            "crp": 0.5,
            "lymphocyte": 35,
            "mcv": 90,
            "rdw": 13.0,
            "alkaline_phosphatase": 70,
            "wbc": 5.5,
            "chronological_age": 45
        }
        
    def test_initialization(self):
        """Test API initialization."""
        # Should have calculator and intervention_manager
        self.assertIsNotNone(self.api.calculator)
        self.assertIsNotNone(self.api.intervention_manager)
        
    def test_calculate_phenoage(self):
        """Test phenoage calculation through API."""
        # Calculate phenoage
        result = self.api.calculate_phenoage(self.biomarker_data)
        
        # Should have expected keys
        self.assertIn("pheno_age", result)
        self.assertIn("mort_score", result)
        self.assertIn("est_dnam_age", result)
        
        # Value should be reasonable
        self.assertGreater(result["pheno_age"], 20)
        self.assertLess(result["pheno_age"], 70)
        
    def test_calculate_percentile(self):
        """Test percentile calculation through API."""
        # Calculate phenoage first
        pheno_age = self.api.calculate_phenoage(self.biomarker_data)["pheno_age"]
        
        # Calculate percentile
        percentile = self.api.calculate_percentile(
            self.biomarker_data["chronological_age"],
            pheno_age
        )
        
        # Value should be between 0 and 100
        self.assertGreaterEqual(percentile, 0)
        self.assertLessEqual(percentile, 100)
        
    def test_get_reference_values(self):
        """Test getting reference values through API."""
        # Get reference values
        references = self.api.get_reference_values(
            self.biomarker_data["chronological_age"]
        )
        
        # Should have expected percentiles
        self.assertIn("10th", references)
        self.assertIn("25th", references)
        self.assertIn("50th", references)
        self.assertIn("75th", references)
        self.assertIn("90th", references)
        
        # 50th percentile should equal chronological age
        self.assertEqual(
            references["50th"],
            self.biomarker_data["chronological_age"]
        )
        
    def test_interpret_percentile(self):
        """Test percentile interpretation through API."""
        # Get interpretation
        interpretation = self.api.interpret_percentile(75)
        
        # Should be a non-empty string
        self.assertTrue(isinstance(interpretation, str))
        self.assertGreater(len(interpretation), 0)
        
    def test_get_bioage_assessment(self):
        """Test getting complete bioage assessment."""
        # Get assessment
        assessment = self.api.get_bioage_assessment(self.biomarker_data)
        
        # Should have expected keys
        expected_keys = [
            "chronological_age", "phenotypic_age", "percentile",
            "age_difference", "age_difference_text", "interpretation",
            "reference_values"
        ]
        for key in expected_keys:
            self.assertIn(key, assessment)
        
        # Values should be consistent
        self.assertEqual(
            assessment["chronological_age"],
            self.biomarker_data["chronological_age"]
        )
        
        # Age difference should match
        expected_diff = assessment["chronological_age"] - assessment["phenotypic_age"]
        self.assertAlmostEqual(assessment["age_difference"], expected_diff, places=4)
        
        # Should have reference values
        self.assertIn("50th", assessment["reference_values"])
        
    def test_rank_interventions(self):
        """Test ranking interventions through API."""
        # Rank interventions
        rankings = self.api.rank_interventions(self.biomarker_data)
        
        # Should have 25 interventions
        self.assertEqual(len(rankings), 25)
        
        # Each ranking should have required keys
        for ranking in rankings:
            self.assertIn("intervention", ranking)
            self.assertIn("delta", ranking)
            
    def test_simulate_interventions(self):
        """Test simulating interventions through API."""
        # Get top interventions
        rankings = self.api.rank_interventions(self.biomarker_data)
        top_interventions = [r["intervention"] for r in rankings[:3]]
        
        # Simulate interventions
        simulation = self.api.simulate_interventions(
            self.biomarker_data,
            top_interventions
        )
        
        # Should have expected keys
        expected_keys = [
            "original_biomarkers", "updated_biomarkers",
            "original_pheno_age", "new_pheno_age", "delta",
            "applied_interventions", "original_percentile",
            "new_percentile", "percentile_change",
            "original_interpretation", "new_interpretation",
            "biomarker_changes"
        ]
        for key in expected_keys:
            self.assertIn(key, simulation)
            
        # Percentile should increase
        self.assertGreater(simulation["new_percentile"], simulation["original_percentile"])
        self.assertGreater(simulation["percentile_change"], 0)
        
        # Phenotypic age should decrease
        self.assertLess(simulation["new_pheno_age"], simulation["original_pheno_age"])
        self.assertLess(simulation["delta"], 0)
        
        # Should have biomarker changes
        self.assertGreater(len(simulation["biomarker_changes"]), 0)
        
    def test_get_complete_assessment(self):
        """Test getting complete assessment including interventions."""
        # Get complete assessment
        assessment = self.api.get_complete_assessment(self.biomarker_data)
        
        # Should have expected keys
        expected_keys = [
            "chronological_age", "phenotypic_age", "percentile",
            "interpretation", "reference_values", "intervention_rankings"
        ]
        for key in expected_keys:
            self.assertIn(key, assessment)
            
        # Should have intervention rankings
        self.assertEqual(len(assessment["intervention_rankings"]), 25)


if __name__ == "__main__":
    unittest.main()
