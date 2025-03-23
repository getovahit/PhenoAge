from .models import InterventionModels


class InterventionManager:
    """
    Manages interventions, including ranking and simulation of their effects on biomarkers.
    """
    
    def __init__(self, calculator):
        """
        Initialize the intervention manager.
        
        Parameters:
        -----------
        calculator : AgeClockCalculator
            An instance of the AgeClockCalculator class for PhenoAge calculations
        """
        self.calculator = calculator
        
    def get_interventions(self):
        """
        Return a list of interventions and the corresponding apply functions
        
        Returns:
        --------
        list
            List of dictionaries containing intervention names and their apply functions
        """
        return [
            {"name": "Regular Exercise", "apply_fn": InterventionModels.apply_exercise},
            {"name": "Weight Loss", "apply_fn": InterventionModels.apply_weight_loss},
            {"name": "Low Allergen Diet", "apply_fn": InterventionModels.apply_low_allergen_diet},
            {"name": "Curcumin (500 mg/day)", "apply_fn": InterventionModels.apply_curcumin},
            {"name": "Omega-3 (1.5–3 g/day)", "apply_fn": InterventionModels.apply_omega3},
            {"name": "Taurine (3–6 g/day)", "apply_fn": InterventionModels.apply_taurine},
            {"name": "High Protein Intake", "apply_fn": InterventionModels.apply_high_protein_diet},
            {"name": "Well-Balanced Diet", "apply_fn": InterventionModels.apply_balanced_diet},
            {"name": "Reduce Alcohol", "apply_fn": InterventionModels.apply_reduce_alcohol},
            {"name": "Stop Creatine Supplementation", "apply_fn": InterventionModels.apply_stop_creatine},
            {"name": "Reduce Red Meat Intake", "apply_fn": InterventionModels.apply_reduce_red_meat},
            {"name": "Reduce Sodium", "apply_fn": InterventionModels.apply_reduce_sodium},
            {"name": "Avoid NSAIDs", "apply_fn": InterventionModels.apply_avoid_nsaids},
            {"name": "Avoid Very Heavy Exercise", "apply_fn": InterventionModels.apply_avoid_heavy_exercise},
            {"name": "Milk Thistle (1 g/day)", "apply_fn": InterventionModels.apply_milk_thistle},
            {"name": "NAC (1–2 g/day)", "apply_fn": InterventionModels.apply_nac},
            {"name": "Carb & Fat Restriction", "apply_fn": InterventionModels.apply_carb_fat_restriction},
            {"name": "Walking After Meals", "apply_fn": InterventionModels.apply_postmeal_walk},
            {"name": "Sauna", "apply_fn": InterventionModels.apply_sauna},
            {"name": "Berberine (500–1000 mg/day)", "apply_fn": InterventionModels.apply_berberine},
            {"name": "Vitamin B1 (100 mg/day)", "apply_fn": InterventionModels.apply_vitb1},
            {"name": "Olive Oil (Med Diet)", "apply_fn": InterventionModels.apply_olive_oil},
            {"name": "Mushrooms (Beta-Glucans)", "apply_fn": InterventionModels.apply_mushrooms},
            {"name": "Zinc Supplementation", "apply_fn": InterventionModels.apply_zinc},
            {"name": "B-Complex (B12/Folate)", "apply_fn": InterventionModels.apply_bcomplex}
        ]
    
    def rank_interventions(self, biomarker_data):
        """
        For the user's current biomarkers, apply each intervention individually,
        recalculate PhenoAge, and see the difference. Sort by the biggest improvement.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        list
            List of dictionaries containing interventions and their impact on PhenoAge,
            sorted by the amount of improvement (biggest improvement first)
        """
        # 1) Calculate baseline
        base_result = self.calculator.calculate_phenoage(biomarker_data)
        base_pheno = base_result["pheno_age"]
        
        # 2) Test each intervention
        ranking = []
        for item in self.get_interventions():
            name = item["name"]
            fn = item["apply_fn"]
            
            # copy biomarkers
            updated = dict(biomarker_data)
            # apply
            updated = fn(updated)
            
            # recalc pheno
            new_res = self.calculator.calculate_phenoage(updated)
            new_pheno = new_res["pheno_age"]
            delta = new_pheno - base_pheno
            ranking.append({
                "intervention": name,
                "base_pheno_age": base_pheno,
                "new_pheno_age": new_pheno,
                "delta": delta
            })
        
        # 3) Sort ascending by delta (lowest final => best improvement)
        ranking.sort(key=lambda x: x["delta"])
        return ranking
    
    def simulate_combined_interventions(self, biomarker_data, interventions):
        """
        Simulate the effect of applying multiple interventions together.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary of biomarker values
        interventions : list
            List of intervention names to apply
            
        Returns:
        --------
        dict
            Dictionary containing original biomarkers, updated biomarkers,
            original PhenoAge, new PhenoAge, and the delta
        """
        # Get mapping of intervention names to functions
        intervention_map = {item["name"]: item["apply_fn"] for item in self.get_interventions()}
        
        # Calculate baseline
        base_result = self.calculator.calculate_phenoage(biomarker_data)
        base_pheno = base_result["pheno_age"]
        
        # Apply each intervention in sequence
        updated = dict(biomarker_data)
        applied_interventions = []
        
        for intervention_name in interventions:
            if intervention_name in intervention_map:
                fn = intervention_map[intervention_name]
                updated = fn(updated)
                applied_interventions.append(intervention_name)
            else:
                raise ValueError(f"Unknown intervention: {intervention_name}")
        
        # Calculate new PhenoAge
        new_res = self.calculator.calculate_phenoage(updated)
        new_pheno = new_res["pheno_age"]
        
        return {
            "original_biomarkers": biomarker_data,
            "updated_biomarkers": updated,
            "original_pheno_age": base_pheno,
            "new_pheno_age": new_pheno,
            "delta": new_pheno - base_pheno,
            "applied_interventions": applied_interventions
        }
