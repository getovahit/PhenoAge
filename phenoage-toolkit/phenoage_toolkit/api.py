from .biomarkers.calculator import AgeClockCalculator
from .percentile.calculator import calculate_percentile, get_reference_values, interpret_percentile
from .interventions.manager import InterventionManager


class PhenoAgeAPI:
    """
    Unified API for PhenoAge calculations, percentile rankings, and intervention simulations.
    
    This provides a single entry point for all functionality of the PhenoAge toolkit.
    """
    
    def __init__(self):
        """Initialize the PhenoAge API with required components."""
        self.calculator = AgeClockCalculator()
        self.intervention_manager = InterventionManager(self.calculator)
    
    def calculate_phenoage(self, biomarker_data):
        """
        Calculate phenotypic age from biomarkers.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values with keys matching required biomarkers.
            
        Returns:
        --------
        dict
            Dictionary with phenotypic age calculation results
        """
        # Use the age clock calculator to get PhenoAge
        result = self.calculator.calculate_phenoage(biomarker_data)
        return result
    
    def calculate_percentile(self, chronological_age, phenotypic_age):
        """
        Calculate percentile rank for a phenotypic age compared to chronological age peers.
        
        Parameters:
        -----------
        chronological_age : float
            Chronological age in years
        phenotypic_age : float
            Phenotypic (biological) age in years
            
        Returns:
        --------
        float
            Percentile value (0-100)
        """
        return calculate_percentile(chronological_age, phenotypic_age)
    
    def get_reference_values(self, chronological_age):
        """
        Get reference phenotypic age values for different percentiles.
        
        Parameters:
        -----------
        chronological_age : float
            Chronological age in years
            
        Returns:
        --------
        dict
            Dictionary with reference values for different percentiles
        """
        return get_reference_values(chronological_age)
    
    def interpret_percentile(self, percentile):
        """
        Provide a human-readable interpretation of a percentile value.
        
        Parameters:
        -----------
        percentile : float
            Percentile value (0-100)
            
        Returns:
        --------
        str
            Human-readable interpretation
        """
        return interpret_percentile(percentile)
    
    def get_bioage_assessment(self, biomarker_data):
        """
        Get a complete assessment of biological age including PhenoAge and percentile.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Complete assessment with phenotypic age, percentile, and interpretation
        """
        # Calculate phenotypic age
        phenoage_result = self.calculate_phenoage(biomarker_data)
        chron_age = float(biomarker_data["chronological_age"])
        pheno_age = phenoage_result["pheno_age"]
        
        # Calculate percentile
        percentile = self.calculate_percentile(chron_age, pheno_age)
        
        # Get interpretation
        interpretation = self.interpret_percentile(percentile)
        
        # Get reference values
        references = self.get_reference_values(chron_age)
        
        # Calculate age difference
        age_diff = chron_age - pheno_age
        if age_diff > 0:
            age_diff_text = f"{age_diff:.1f} years YOUNGER than chronological age"
        elif age_diff < 0:
            age_diff_text = f"{abs(age_diff):.1f} years OLDER than chronological age"
        else:
            age_diff_text = "exactly matching chronological age"
        
        # Compile the assessment
        assessment = {
            "chronological_age": chron_age,
            "phenotypic_age": pheno_age,
            "percentile": percentile,
            "age_difference": age_diff,
            "age_difference_text": age_diff_text,
            "interpretation": interpretation,
            "reference_values": references
        }
        
        return assessment
    
    def rank_interventions(self, biomarker_data):
        """
        Rank potential interventions by their impact on reducing phenotypic age.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        list
            Ranked list of interventions with their impact
        """
        return self.intervention_manager.rank_interventions(biomarker_data)
    
    def simulate_interventions(self, biomarker_data, selected_interventions):
        """
        Simulate the effect of selected interventions on biomarkers and phenotypic age.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
        selected_interventions : list
            List of intervention names to simulate
            
        Returns:
        --------
        dict
            Results of intervention simulation with before/after comparisons
        """
        # Simulate interventions
        simulation = self.intervention_manager.simulate_combined_interventions(
            biomarker_data, selected_interventions
        )
        
        # Get original percentile
        original_pheno = simulation["original_pheno_age"]
        chron_age = float(biomarker_data["chronological_age"])
        original_percentile = self.calculate_percentile(chron_age, original_pheno)
        
        # Get new percentile
        new_pheno = simulation["new_pheno_age"]
        new_percentile = self.calculate_percentile(chron_age, new_pheno)
        
        # Add percentile information to the simulation results
        simulation["original_percentile"] = original_percentile
        simulation["new_percentile"] = new_percentile
        simulation["percentile_change"] = new_percentile - original_percentile
        simulation["original_interpretation"] = self.interpret_percentile(original_percentile)
        simulation["new_interpretation"] = self.interpret_percentile(new_percentile)
        
        # Format biomarker changes for clear reporting
        biomarker_changes = []
        for biomarker in simulation["original_biomarkers"]:
            orig_value = simulation["original_biomarkers"][biomarker]
            new_value = simulation["updated_biomarkers"][biomarker]
            
            if orig_value != new_value:
                biomarker_changes.append({
                    "biomarker": biomarker,
                    "original_value": orig_value,
                    "new_value": new_value,
                    "change": new_value - orig_value,
                    "percent_change": (new_value - orig_value) / orig_value * 100 if orig_value != 0 else float('inf')
                })
        
        simulation["biomarker_changes"] = biomarker_changes
        
        return simulation

    def get_complete_assessment(self, biomarker_data):
        """
        Get a complete assessment including phenotypic age, percentile, and intervention rankings.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Complete assessment with all information
        """
        # Get the basic assessment
        assessment = self.get_bioage_assessment(biomarker_data)
        
        # Add intervention rankings
        assessment["intervention_rankings"] = self.rank_interventions(biomarker_data)
        
        return assessment
