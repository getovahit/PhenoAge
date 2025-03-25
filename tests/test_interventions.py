"""
Unit tests for the interventions module.
"""

import unittest
from phenoage_toolkit.interventions.models import InterventionModels
from phenoage_toolkit.interventions.manager import InterventionManager
from phenoage_toolkit.biomarkers.calculator import AgeClockCalculator


class TestInterventionModels(unittest.TestCase):
    """Test the InterventionModels class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample biomarker data with elevated markers
        self.elevated_biomarkers = {
            "albumin": 3.8,             # Low albumin
            "creatinine": 1.2,          # High creatinine
            "glucose": 110,             # High glucose
            "crp": 3.5,                 # High CRP
            "lymphocyte": 25,           # Low lymphocyte
            "mcv": 95,                  # Normal MCV
            "rdw": 14.5,                # Normal RDW
            "alkaline_phosphatase": 120, # High ALP
            "wbc": 8.5,                 # High WBC
            "chronological_age": 45     # Age
        }
        
        # Sample biomarker data with normal markers
        self.normal_biomarkers = {
            "albumin": 4.5,             # Normal albumin
            "creatinine": 0.9,          # Normal creatinine
            "glucose": 85,              # Normal glucose
            "crp": 0.5,                 # Normal CRP
            "lymphocyte": 35,           # Normal lymphocyte
            "mcv": 90,                  # Normal MCV
            "rdw": 13.0,                # Normal RDW
            "alkaline_phosphatase": 65, # Normal ALP
            "wbc": 5.5,                 # Normal WBC
            "chronological_age": 45     # Age
        }
        
    def test_clamp_function(self):
        """Test the clamp utility function."""
        # Test clamping to minimum
        self.assertEqual(InterventionModels.clamp(5, 10), 10)
        self.assertEqual(InterventionModels.clamp(-5, 0), 0)
        
        # Test no clamping needed
        self.assertEqual(InterventionModels.clamp(15, 10), 15)
        
        # Test clamping to maximum
        self.assertEqual(InterventionModels.clamp(15, 0, 10), 10)
        
        # Test no clamping needed within range
        self.assertEqual(InterventionModels.clamp(5, 0, 10), 5)
        
    def test_intervention_exercise(self):
        """Test the exercise intervention."""
        # Apply to elevated biomarkers
        result = InterventionModels.apply_exercise(self.elevated_biomarkers)
        
        # Should reduce CRP
        self.assertLess(result["crp"], self.elevated_biomarkers["crp"])
        
        # Should reduce glucose
        self.assertLess(result["glucose"], self.elevated_biomarkers["glucose"])
        
        # Should reduce WBC if elevated
        self.assertLess(result["wbc"], self.elevated_biomarkers["wbc"])
        
        # Should increase lymphocyte if low
        self.assertGreater(result["lymphocyte"], self.elevated_biomarkers["lymphocyte"])
        
        # Apply to normal biomarkers
        result_normal = InterventionModels.apply_exercise(self.normal_biomarkers)
        
        # Should have smaller effect on normal CRP
        crp_reduction_elevated = self.elevated_biomarkers["crp"] - result["crp"]
        crp_reduction_normal = self.normal_biomarkers["crp"] - result_normal["crp"]
        self.assertGreater(crp_reduction_elevated, crp_reduction_normal)
        
    def test_intervention_weight_loss(self):
        """Test the weight loss intervention."""
        # Apply to elevated biomarkers
        result = InterventionModels.apply_weight_loss(self.elevated_biomarkers)
        
        # Should reduce CRP
        self.assertLess(result["crp"], self.elevated_biomarkers["crp"])
        
        # Should reduce glucose
        self.assertLess(result["glucose"], self.elevated_biomarkers["glucose"])
        
        # Should reduce WBC if elevated
        self.assertLess(result["wbc"], self.elevated_biomarkers["wbc"])
        
    def test_intervention_curcumin(self):
        """Test the curcumin intervention."""
        # Apply to elevated biomarkers (high CRP)
        result = InterventionModels.apply_curcumin(self.elevated_biomarkers)
        
        # Should significantly reduce CRP
        self.assertLess(result["crp"], self.elevated_biomarkers["crp"])
        self.assertGreaterEqual(
            self.elevated_biomarkers["crp"] - result["crp"], 
            1.0  # Should reduce by at least 1.0
        )
        
        # Apply to normal biomarkers (low CRP)
        result_normal = InterventionModels.apply_curcumin(self.normal_biomarkers)
        
        # Should have smaller effect on normal CRP
        crp_reduction_elevated = self.elevated_biomarkers["crp"] - result["crp"]
        crp_reduction_normal = self.normal_biomarkers["crp"] - result_normal["crp"]
        self.assertGreater(crp_reduction_elevated, crp_reduction_normal)
        
    def test_intervention_omega3(self):
        """Test the omega-3 intervention."""
        # Apply to elevated biomarkers
        result = InterventionModels.apply_omega3(self.elevated_biomarkers)
        
        # Should reduce CRP
        self.assertLess(result["crp"], self.elevated_biomarkers["crp"])
        
        # Should reduce WBC if elevated
        self.assertLess(result["wbc"], self.elevated_biomarkers["wbc"])
        
        # Should increase albumin if low
        self.assertGreater(result["albumin"], self.elevated_biomarkers["albumin"])
        
        # Should increase lymphocyte if low
        self.assertGreater(result["lymphocyte"], self.elevated_biomarkers["lymphocyte"])
        
    def test_minimum_floor_values(self):
        """Test that interventions don't reduce values below sensible floors."""
        # Create biomarkers with very low values
        low_biomarkers = self.normal_biomarkers.copy()
        low_biomarkers["crp"] = 0.05  # Very low CRP
        low_biomarkers["glucose"] = 75  # Low glucose
        
        # Apply interventions that reduce these markers
        result = InterventionModels.apply_exercise(low_biomarkers)
        
        # Should not reduce below sensible minimum
        self.assertGreaterEqual(result["crp"], 0.01)
        self.assertGreaterEqual(result["glucose"], 70)
        
    def test_all_intervention_methods_exist(self):
        """Test that all 25 intervention methods exist."""
        # Get all method names that start with 'apply_'
        intervention_methods = [
            method for method in dir(InterventionModels)
            if method.startswith('apply_') and callable(getattr(InterventionModels, method))
        ]
        
        # Should have at least 25 intervention methods
        self.assertGreaterEqual(len(intervention_methods), 25)
        
    def test_all_interventions_preserve_biomarkers(self):
        """Test that all interventions preserve the biomarker keys."""
        # Get all method names that start with 'apply_'
        intervention_methods = [
            method for method in dir(InterventionModels)
            if method.startswith('apply_') and callable(getattr(InterventionModels, method))
        ]
        
        # Test each intervention method
        for method_name in intervention_methods:
            method = getattr(InterventionModels, method_name)
            
            # Apply the intervention
            result = method(self.elevated_biomarkers)
            
            # Should have all original biomarker keys
            for key in self.elevated_biomarkers:
                self.assertIn(key, result)
                
            # Values should be of the same type (float)
            for key in result:
                if key in self.elevated_biomarkers:
                    self.assertIsInstance(result[key], type(self.elevated_biomarkers[key]))


class TestInterventionManager(unittest.TestCase):
    """Test the InterventionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create dependencies
        self.calculator = AgeClockCalculator()
        self.manager = InterventionManager(self.calculator)
        
        # Sample biomarker data
        self.biomarker_data = {
            "albumin": 4.0,
            "creatinine": 1.0,
            "glucose": 100,
            "crp": 1.0,
            "lymphocyte": 30,
            "mcv": 90,
            "rdw": 14.0,
            "alkaline_phosphatase": 80,
            "wbc": 6.0,
            "chronological_age": 50
        }
        
    def test_get_interventions(self):
        """Test getting the list of interventions."""
        interventions = self.manager.get_interventions()
        
        # Should have 25 interventions
        self.assertEqual(len(interventions), 25)
        
        # Each intervention should have name and apply_fn
        for intervention in interventions:
            self.assertIn("name", intervention)
            self.assertIn("apply_fn", intervention)
            self.assertTrue(callable(intervention["apply_fn"]))
            
    def test_rank_interventions(self):
        """Test ranking interventions."""
        # Rank interventions
        rankings = self.manager.rank_interventions(self.biomarker_data)
        
        # Should have 25 rankings
        self.assertEqual(len(rankings), 25)
        
        # Each ranking should have required keys
        for ranking in rankings:
            self.assertIn("intervention", ranking)
            self.assertIn("base_pheno_age", ranking)
            self.assertIn("new_pheno_age", ranking)
            self.assertIn("delta", ranking)
            
        # Rankings should be sorted by delta (ascending)
        for i in range(len(rankings) - 1):
            self.assertLessEqual(rankings[i]["delta"], rankings[i+1]["delta"])
            
        # All should have the same base_pheno_age
        base_pheno = rankings[0]["base_pheno_age"]
        for ranking in rankings:
            self.assertEqual(ranking["base_pheno_age"], base_pheno)
            
    def test_simulate_combined_interventions(self):
        """Test simulating combined interventions."""
        # Select top 3 interventions
        rankings = self.manager.rank_interventions(self.biomarker_data)
        top_interventions = [r["intervention"] for r in rankings[:3]]
        
        # Simulate combined interventions
        result = self.manager.simulate_combined_interventions(
            self.biomarker_data, 
            top_interventions
        )
        
        # Should have required keys
        self.assertIn("original_biomarkers", result)
        self.assertIn("updated_biomarkers", result)
        self.assertIn("original_pheno_age", result)
        self.assertIn("new_pheno_age", result)
        self.assertIn("delta", result)
        self.assertIn("applied_interventions", result)
        
        # Should have applied all interventions
        self.assertEqual(len(result["applied_interventions"]), 3)
        for intervention in top_interventions:
            self.assertIn(intervention, result["applied_interventions"])
            
        # Should have reduced phenotypic age
        self.assertLess(result["new_pheno_age"], result["original_pheno_age"])
        self.assertLess(result["delta"], 0)  # Delta should be negative (improvement)
        
        # Updated biomarkers should differ from original
        self.assertNotEqual(result["original_biomarkers"], result["updated_biomarkers"])
        
    def test_simulate_nonexistent_intervention(self):
        """Test handling of nonexistent intervention names."""
        # Try to simulate a nonexistent intervention
        with self.assertRaises(ValueError):
            self.manager.simulate_combined_interventions(
                self.biomarker_data, 
                ["Nonexistent Intervention"]
            )
            
    def test_combined_effect_vs_individual_effects(self):
        """Test that combined effect is not just the sum of individual effects."""
        # Get top 2 interventions
        rankings = self.manager.rank_interventions(self.biomarker_data)
        top_interventions = [r["intervention"] for r in rankings[:2]]
        
        # Get individual effects
        individual_deltas = [r["delta"] for r in rankings[:2]]
        individual_sum = sum(individual_deltas)
        
        # Get combined effect
        combined = self.manager.simulate_combined_interventions(
            self.biomarker_data, 
            top_interventions
        )
        combined_delta = combined["delta"]
        
        # Combined effect should be smaller (more negative) than sum, but not double
        self.assertLess(combined_delta, individual_sum)
        self.assertLess(combined_delta, 2 * individual_deltas[0])


if __name__ == "__main__":
    unittest.main()