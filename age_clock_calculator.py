import pandas as pd
import math
import os
import sys
import json
import numpy as np

class AgeClockCalculator:
    """
    A calculator for various biological age clocks based on biomarker data.
    
    This class can be used in two ways:
    1. Process TSV files containing biomarker data
    2. Calculate age clocks directly from biomarker data passed as dictionaries
    
    The second method is recommended for production pipeline integration.
    """
    
    def __init__(self):
        # Initialize with known age clocks
        self.available_clocks = ["phenoage"]
        
        # Standard biomarker names and their acceptable aliases
        self.biomarker_aliases = {
            "albumin": ["albumin", "alb"],
            "creatinine": ["creatinine", "creat"],
            "glucose": ["glucose", "glu"],
            "crp": ["crp", "c-reactive protein", "c reactive protein"],
            "lymphocyte": ["lymphocyte", "lymph", "lymphocyte percentage", "lymphs", "lymphocytes"],
            "mcv": ["mcv", "mean cell volume", "mean corpuscular volume"],
            "rdw": ["rdw", "red cell distribution width", "rcdw"],
            "alkaline_phosphatase": ["alkaline phosphatase", "alp", "alk phos"],
            "wbc": ["wbc", "white blood cells", "white blood cell count"],
            "chronological_age": ["chronological age", "age", "chron age"]
        }
        
        # Expected units for each biomarker to display in errors/warnings
        self.expected_units = {
            "albumin": "g/dL",
            "creatinine": "mg/dL",
            "glucose": "mg/dL",
            "crp": "mg/L",
            "lymphocyte": "%",
            "mcv": "fL",
            "rdw": "%",
            "alkaline_phosphatase": "U/L",
            "wbc": "10^3 cells/µL",  # Fixed unit from mL to µL
            "chronological_age": "years"
        }
        
        # Constants used in calculations
        self.constants = {
            "phenoage": {
                "t": 10,  # years
                "g": 0.0077,
                "intercept": -19.9067
            }
        }
    
    def normalize_biomarker_name(self, name):
        """
        Convert biomarker name to its standardized form using aliases.
        
        Parameters:
        -----------
        name : str
            The biomarker name to normalize
            
        Returns:
        --------
        str
            Standardized biomarker name or the original if no match found
        """
        name_lower = name.lower().strip()
        
        for standard_name, aliases in self.biomarker_aliases.items():
            if name_lower in [alias.lower() for alias in aliases]:
                return standard_name
                
        return name_lower
    
    def calculate_all_clocks(self, biomarker_data):
        """
        Calculate all available age clocks for the given biomarker data.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary containing biomarker values with their names as keys
            
        Returns:
        --------
        dict
            Dictionary containing results for all available age clocks
        """
        results = {}
        
        # Normalize biomarker names
        normalized_data = {}
        for key, value in biomarker_data.items():
            normalized_key = self.normalize_biomarker_name(key)
            normalized_data[normalized_key] = value
        
        for clock in self.available_clocks:
            if clock == "phenoage":
                results[clock] = self.calculate_phenoage(normalized_data)
        
        return results
    
    def calculate_phenoage(self, biomarker_data):
        """
        Calculate the PhenoAge clock based on the Levine et al. method.
        
        Parameters:
        -----------
        biomarker_data : dict
            Dictionary containing the following normalized biomarkers:
            - albumin (g/dL)
            - creatinine (mg/dL)
            - glucose (mg/dL)
            - crp (mg/L)
            - lymphocyte (%)
            - mcv (fL)
            - rdw (%)
            - alkaline_phosphatase (U/L)
            - wbc (10^3 cells/µL)
            - chronological_age (years)
            
        Returns:
        --------
        dict
            Dictionary containing PhenoAge results
        """
        # Ensure all required biomarkers are present
        required_biomarkers = [
            "albumin", "creatinine", "glucose", "crp", "lymphocyte", 
            "mcv", "rdw", "alkaline_phosphatase", "wbc", "chronological_age"
        ]
        
        missing_biomarkers = []
        for biomarker in required_biomarkers:
            if biomarker not in biomarker_data:
                missing_biomarkers.append(f"{biomarker} ({self.expected_units[biomarker]})")
        
        if missing_biomarkers:
            raise ValueError(f"Missing required biomarkers: {', '.join(missing_biomarkers)}")
        
        # Extract biomarker values
        albumin = float(biomarker_data["albumin"])
        creatinine = float(biomarker_data["creatinine"])
        glucose = float(biomarker_data["glucose"])
        crp = float(biomarker_data["crp"])
        lymphocyte = float(biomarker_data["lymphocyte"])
        mcv = float(biomarker_data["mcv"])
        rdw = float(biomarker_data["rdw"])
        alkaline_phosphatase = float(biomarker_data["alkaline_phosphatase"])
        wbc = float(biomarker_data["wbc"])
        chronological_age = float(biomarker_data["chronological_age"])
        
        # Convert units to the required format
        albumin_converted = albumin * 10  # g/dL to g/L
        creatinine_converted = creatinine * 88.4  # mg/dL to μmol/L
        glucose_converted = glucose * 0.0555  # mg/dL to mmol/L
        
        # Apply CRP safeguard for log calculation
        crp_for_calc = (crp * 0.1)  # mg/L to mg/dL
        if crp_for_calc <= 0:  # safeguard for log calculation
            crp_for_calc = 0.000001
        crp_converted = np.log(crp_for_calc)
        
        lymphocyte_converted = lymphocyte  # % stays as %
        mcv_converted = mcv  # fL stays as fL
        rdw_converted = rdw  # % stays as %
        alkaline_phosphatase_converted = alkaline_phosphatase  # U/L stays as U/L
        wbc_converted = wbc  # 10^3 cells/µL stays as is
        chronological_age_converted = chronological_age  # years stays as years
        
        # Weights from the PhenoAge model
        albumin_weight = -0.0336
        creatinine_weight = 0.0095
        glucose_weight = 0.1953
        crp_weight = 0.0954
        lymphocyte_weight = -0.0120
        mcv_weight = 0.0268
        rdw_weight = 0.3306
        alkaline_phosphatase_weight = 0.0019
        wbc_weight = 0.0554
        chronological_age_weight = 0.0804
        intercept = self.constants["phenoage"]["intercept"]
        
        # Calculate the terms
        albumin_term = albumin_converted * albumin_weight
        creatinine_term = creatinine_converted * creatinine_weight
        glucose_term = glucose_converted * glucose_weight
        crp_term = crp_converted * crp_weight
        lymphocyte_term = lymphocyte_converted * lymphocyte_weight
        mcv_term = mcv_converted * mcv_weight
        rdw_term = rdw_converted * rdw_weight
        alkaline_phosphatase_term = alkaline_phosphatase_converted * alkaline_phosphatase_weight
        wbc_term = wbc_converted * wbc_weight
        chronological_age_term = chronological_age_converted * chronological_age_weight
        
        # Calculate linear combination
        lin_comb = (
            albumin_term + creatinine_term + glucose_term + crp_term + 
            lymphocyte_term + mcv_term + rdw_term + alkaline_phosphatase_term + 
            wbc_term + chronological_age_term + intercept
        )
        
        # Constants
        t = 120  # 10 years in months
        g = 0.0076927  # gamma from the original formula
        
        # Calculate mortality score
        # Formula: MortScore = 1-EXP(-EXP(LinComb)*(EXP(g*t)-1)/g)
        mort_score = 1 - math.exp(-math.exp(lin_comb) * (math.exp(g * t) - 1) / g)
        
        # Calculate phenoage (in years)
        # Formula: PhenoAge = 141.50225+LN(-0.00553*LN(1-MortScore))/0.090165
        pheno_age = 141.50225 + math.log(-0.00553 * math.log(1 - mort_score)) / 0.090165
        
        # Calculate estimated DNAm Age
        # Formula: estDNAm Age = PhenoAge/(1+1.28047*EXP(0.0344329*(-182.344+PhenoAge)))
        est_dnam_age = pheno_age / (1 + 1.28047 * math.exp(0.0344329 * (-182.344 + pheno_age)))
        
        # Calculate estimated D MScore
        # Formula: est D MScore = 1-EXP(-0.000520363523*EXP(0.090165*DNAm Age))
        est_d_mscore = 1 - math.exp(-0.000520363523 * math.exp(0.090165 * est_dnam_age))
        
        # Return all results
        return {
            "lin_comb": lin_comb,
            "mort_score": mort_score,
            "pheno_age": pheno_age,
            "est_dnam_age": est_dnam_age,
            "est_d_mscore": est_d_mscore,
            "terms": {
                "albumin": albumin_term,
                "creatinine": creatinine_term,
                "glucose": glucose_term,
                "crp": crp_term,
                "lymphocyte": lymphocyte_term,
                "mcv": mcv_term,
                "rdw": rdw_term,
                "alkaline_phosphatase": alkaline_phosphatase_term,
                "wbc": wbc_term,
                "chronological_age": chronological_age_term
            },
            "inputs": {
                "albumin": albumin,
                "creatinine": creatinine,
                "glucose": glucose,
                "crp": crp,
                "lymphocyte": lymphocyte,
                "mcv": mcv,
                "rdw": rdw,
                "alkaline_phosphatase": alkaline_phosphatase,
                "wbc": wbc,
                "chronological_age": chronological_age
            },
            "converted_inputs": {
                "albumin": albumin_converted,
                "creatinine": creatinine_converted,
                "glucose": glucose_converted,
                "crp": crp_converted,
                "lymphocyte": lymphocyte_converted,
                "mcv": mcv_converted,
                "rdw": rdw_converted,
                "alkaline_phosphatase": alkaline_phosphatase_converted,
                "wbc": wbc_converted,
                "chronological_age": chronological_age_converted
            }
        }

    def process_direct_input(self, biomarker_data_list):
        """
        Process a list of biomarker data dictionaries directly (no file input).
        This method is ideal for pipeline integration.
        
        Parameters:
        -----------
        biomarker_data_list : list of dict or dict
            List of dictionaries containing biomarker data for each subject.
            Each dictionary should contain biomarker names and values.
            If a single dictionary is provided, it will be treated as a single subject.
            
        Returns:
        --------
        list of dict
            List of dictionaries containing input biomarkers and calculated age clocks for each subject
        """
        # Convert single dictionary to list for consistent processing
        if isinstance(biomarker_data_list, dict):
            biomarker_data_list = [biomarker_data_list]
            
        # Calculate age clocks for each subject
        results_list = []
        for subject_data in biomarker_data_list:
            try:
                subject_results = self.calculate_all_clocks(subject_data)
                
                # Create a result dictionary with original biomarkers and calculated clocks
                result_row = subject_data.copy()
                
                # Add calculated clocks
                for clock_name, clock_results in subject_results.items():
                    for metric, value in clock_results.items():
                        # Only include the main metrics in the output
                        if metric in ['lin_comb', 'mort_score', 'pheno_age', 'est_dnam_age', 'est_d_mscore']:
                            result_row[f"{clock_name}_{metric}"] = value
                
                results_list.append(result_row)
            except Exception as e:
                # Add error message to the row
                error_row = subject_data.copy()
                error_row['error'] = str(e)
                results_list.append(error_row)
        
        return results_list

    def read_tsv_file(self, file_path):
        """
        Read a TSV file and return a list of dictionaries with biomarker data.
        
        Parameters:
        -----------
        file_path : str
            Path to the TSV file
            
        Returns:
        --------
        list of dict
            List of dictionaries containing biomarker data
        """
        try:
            df = pd.read_csv(file_path, sep='\t')
            
            # Check if the dataframe is empty
            if df.empty:
                raise ValueError("The TSV file is empty")
            
            # Process each row into a dictionary of biomarker data
            biomarker_data_list = []
            for _, row in df.iterrows():
                biomarker_data = {}
                for column in df.columns:
                    if pd.notna(row[column]):  # Skip NaN values
                        biomarker_data[column] = row[column]
                biomarker_data_list.append(biomarker_data)
            
            return biomarker_data_list
            
        except Exception as e:
            raise Exception(f"Error reading TSV file: {str(e)}")

    def process_tsv_file(self, file_path, output_path=None, output_format='tsv', generate_rankings=False, apply_interventions=None):
        """
        Process a TSV file and calculate age clocks for each row.
        
        Parameters:
        -----------
        file_path : str
            Path to the input TSV file
        output_path : str, optional
            Path to save the output file (default: None, returns DataFrame)
        output_format : str, optional
            Format to save the output file ('tsv', 'csv', 'excel', 'json') (default: 'tsv')
        generate_rankings : bool, optional
            Generate intervention rankings for each individual (default: False)
        apply_interventions : str, optional
            Comma-separated list of interventions to apply to each individual (default: None)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing input biomarkers and calculated age clocks
        """
        try:
            # Read the TSV file
            biomarker_data_list = self.read_tsv_file(file_path)
            
            # Process the biomarker data using the direct input method
            results_list = self.process_direct_input(biomarker_data_list)
            
            # If rankings requested, generate for each individual
            if generate_rankings:
                print(f"Generating intervention rankings for {len(results_list)} individuals...")
                for i, row in enumerate(results_list):
                    # Skip rows with errors
                    if 'error' in row:
                        continue
                        
                    # Extract biomarker data for this person
                    biomarkers = {
                        "albumin": row["albumin"],
                        "creatinine": row["creatinine"],
                        "glucose": row["glucose"],
                        "crp": row["crp"],
                        "lymphocyte": row["lymphocyte"],
                        "mcv": row["mcv"],
                        "rdw": row["rdw"],
                        "alkaline_phosphatase": row["alkaline_phosphatase"],
                        "wbc": row["wbc"],
                        "chronological_age": row["chronological_age"]
                    }
                    
                    # Get top 5 intervention rankings
                    try:
                        rankings = self.rank_interventions(biomarkers)[:5]
                        for j, rank in enumerate(rankings):
                            results_list[i][f"rank{j+1}_intervention"] = rank["intervention"]
                            results_list[i][f"rank{j+1}_impact"] = -rank["delta"]  # Convert to positive number
                    except Exception as e:
                        results_list[i]["ranking_error"] = str(e)
            
            # If specific interventions should be applied
            if apply_interventions:
                print(f"Applying interventions to {len(results_list)} individuals...")
                intervention_list = [i.strip() for i in apply_interventions.split(",")]
                
                for i, row in enumerate(results_list):
                    # Skip rows with errors
                    if 'error' in row:
                        continue
                        
                    # Extract biomarker data for this person
                    biomarkers = {
                        "albumin": row["albumin"],
                        "creatinine": row["creatinine"],
                        "glucose": row["glucose"],
                        "crp": row["crp"],
                        "lymphocyte": row["lymphocyte"],
                        "mcv": row["mcv"],
                        "rdw": row["rdw"],
                        "alkaline_phosphatase": row["alkaline_phosphatase"],
                        "wbc": row["wbc"],
                        "chronological_age": row["chronological_age"]
                    }
                    
                    # Apply combined interventions
                    try:
                        combined = self.simulate_combined_interventions(biomarkers, intervention_list)
                        
                        # Add results
                        results_list[i]["combined_pheno_age"] = combined["new_pheno_age"]
                        results_list[i]["years_younger"] = -combined["delta"]
                        
                        # Add biomarker changes 
                        for biomarker in biomarkers:
                            if biomarkers[biomarker] != combined["updated_biomarkers"][biomarker]:
                                old_val = biomarkers[biomarker]
                                new_val = combined["updated_biomarkers"][biomarker]
                                results_list[i][f"{biomarker}_new"] = new_val
                                results_list[i][f"{biomarker}_change"] = new_val - old_val
                    except Exception as e:
                        results_list[i]["intervention_error"] = str(e)
            
            # Convert to DataFrame
            results_df = pd.DataFrame(results_list)
            
            # Save to file if output_path is provided
            if output_path:
                directory = os.path.dirname(output_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    
                if output_format.lower() == 'tsv':
                    results_df.to_csv(output_path, sep='\t', index=False)
                elif output_format.lower() == 'csv':
                    results_df.to_csv(output_path, index=False)
                elif output_format.lower() == 'excel':
                    results_df.to_excel(output_path, index=False)
                elif output_format.lower() == 'json':
                    # Convert DataFrame to list of dictionaries
                    results_json = results_df.to_dict(orient='records')
                    with open(output_path, 'w') as f:
                        json.dump(results_json, f, indent=2)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
            
            return results_df
            
        except Exception as e:
            raise Exception(f"Error processing TSV file: {str(e)}")

    # -------------- NEW CODE BELOW: Interventions + Ranking --------------

    # UTILITY: clamp function to avoid negative or nonsensical values
    def clamp(self, val, minv, maxv=None):
        """
        Utility function to clamp a value between minimum and maximum values
        
        Parameters:
        -----------
        val : float
            Value to clamp
        minv : float
            Minimum allowed value
        maxv : float, optional
            Maximum allowed value (default: None)
            
        Returns:
        --------
        float
            Clamped value
        """
        if val < minv:
            return minv
        if maxv is not None and val > maxv:
            return maxv
        return val

    def apply_exercise(self, biomarkers):
        """
        Regular Exercise: lowers CRP significantly if CRP is high, lowers Glucose,
        can reduce WBC if elevated, can bump lymphocyte%, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        
        # hsCRP logic (from references: can drop CRP by ~6–8 mg/L in overweight w/ high CRP)
        crp = new_vals["crp"]
        if crp >= 3.0:
            # large drop, e.g. ~3 mg/L
            new_vals["crp"] = self.clamp(crp - 3.0, 0.01)
        elif crp >= 1.0:
            # moderate drop
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        else:
            # if CRP <1, small drop
            new_vals["crp"] = self.clamp(crp - 0.2, 0.01)
        
        # Glucose: ~5–15 mg/dL drop, bigger if baseline is high
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = self.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = self.clamp(glu - 7, 70)
        else:
            new_vals["glucose"] = self.clamp(glu - 3, 70)
        
        # WBC: if high, reduce by 1.0
        wbc = new_vals["wbc"]
        if wbc >= 8.0:
            new_vals["wbc"] = max(wbc - 1.0, 4.0)
        
        # Lymphocyte%: might rise a few points if it was low
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = self.clamp(lymph + 5, 5, 60)
        else:
            new_vals["lymphocyte"] = lymph  # no big effect if already normal

        return new_vals

    def apply_weight_loss(self, biomarkers):
        """
        Weight Loss: ~10% body weight loss => 30–40% CRP drop, 5–20 mg/dL glucose drop, lowers WBC, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        
        # CRP
        crp = new_vals["crp"]
        # If CRP is e.g. 4 mg/L => 30–40% => ~1.5 mg/L drop. We'll do piecewise:
        if crp >= 5.0:
            new_vals["crp"] = self.clamp(crp - 2.0, 0.01)
        elif crp >= 2.0:
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        else:
            new_vals["crp"] = self.clamp(crp - 0.2, 0.01)
        
        # Glucose
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = self.clamp(glu - 20, 70)
        elif glu >= 100:
            new_vals["glucose"] = self.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = self.clamp(glu - 3, 70)
        
        # WBC if high
        wbc = new_vals["wbc"]
        if wbc > 7.5:
            new_vals["wbc"] = max(wbc - 1.0, 4.0)
        
        return new_vals

    def apply_low_allergen_diet(self, biomarkers):
        """
        Low-Allergen / Anti-Inflammatory Diet:
        CRP can drop ~0.2–0.5 mg/L if mild, more if truly inflamed.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = self.clamp(crp - 0.5, 0.01)
        else:
            new_vals["crp"] = self.clamp(crp - 0.2, 0.01)
        return new_vals

    def apply_curcumin(self, biomarkers):
        """
        Curcumin (500–1000 mg/day):
        Lowers CRP by ~3.7 mg/L if CRP is high, or ~0.3 mg/L if low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = self.clamp(crp - 3.7, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        else:
            # already quite low => maybe 0.2 mg/L
            new_vals["crp"] = self.clamp(crp - 0.2, 0.01)
        return new_vals

    def apply_omega3(self, biomarkers):
        """
        Omega-3 (1.5–3 g/day):
        CRP down ~2–3 mg/L if CRP is high (>=5). If CRP <1, maybe ~0.3 mg/L.
        Also can reduce WBC if it's high. Might raise lymph% a bit.
        Albumin can slightly rise in inflammatory states.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 5.0:
            new_vals["crp"] = self.clamp(crp - 3.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        else:
            new_vals["crp"] = self.clamp(crp - 0.3, 0.01)
        
        wbc = new_vals["wbc"]
        if wbc >= 8.0:
            new_vals["wbc"] = max(wbc - 0.8, 4.0)
        
        # If albumin <4.0 and cause is inflammation, might raise it ~0.2
        albumin = new_vals["albumin"]
        if albumin < 4.0:
            new_vals["albumin"] = min(albumin + 0.2, 5.0)

        # Might raise lymph% if it was low
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = self.clamp(lymph + 3, 5, 60)
        
        return new_vals

    def apply_taurine(self, biomarkers):
        """
        Taurine (3–6 g/day):
        ~16–29% CRP drop in diabetics, let's do ~0.4 mg/L if CRP moderate.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = self.clamp(crp - 1.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = self.clamp(crp - 0.4, 0.01)
        else:
            new_vals["crp"] = self.clamp(crp - 0.1, 0.01)
        return new_vals

    def apply_high_protein_diet(self, biomarkers):
        """
        High Protein Intake: raises albumin by 0.2–0.5 g/dL if albumin is low (<4.0).
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alb = new_vals["albumin"]
        if alb < 4.0:
            # raise by e.g. 0.3
            new_vals["albumin"] = min(alb + 0.3, 5.0)
        return new_vals

    def apply_reduce_alcohol(self, biomarkers):
        """
        Reduce Alcohol:
        Can raise albumin if it was low, can lower ALP if it was high.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alb = new_vals["albumin"]
        alp = new_vals["alkaline_phosphatase"]
        
        # If albumin <4 => can rebound by ~0.5
        if alb < 4.0:
            new_vals["albumin"] = min(alb + 0.5, 5.0)
        
        # If ALP >120 => can drop 20–60
        if alp > 120:
            new_vals["alkaline_phosphatase"] = max(alp - 40, 50)
        elif alp > 100:
            new_vals["alkaline_phosphatase"] = max(alp - 20, 50)
        
        return new_vals

    def apply_stop_creatine(self, biomarkers):
        """
        Stop Creatine Supplementation:
        Lowers creatinine by ~0.2–0.3 mg/dL if user was taking it.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        new_vals["creatinine"] = max(creat - 0.25, 0.6)
        return new_vals

    def apply_reduce_red_meat(self, biomarkers):
        """
        Reduce Red Meat Intake:
        Can lower creatinine by ~0.1–0.4 mg/dL
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        # if quite high => bigger drop
        if creat >= 1.2:
            new_vals["creatinine"] = max(creat - 0.3, 0.6)
        else:
            new_vals["creatinine"] = max(creat - 0.1, 0.6)
        return new_vals

    def apply_reduce_sodium(self, biomarkers):
        """
        Reduce Sodium:
        Might improve creatinine by 0.1–0.2 mg/dL in borderline CKD
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        if creat >= 1.2:
            new_vals["creatinine"] = max(creat - 0.2, 0.6)
        else:
            new_vals["creatinine"] = max(creat - 0.1, 0.6)
        return new_vals

    def apply_avoid_nsaids(self, biomarkers):
        """
        Avoid NSAIDs:
        Can reduce creatinine by ~0.1–0.3 mg/dL if it was elevated from NSAIDs.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        new_vals["creatinine"] = max(creat - 0.2, 0.6)
        return new_vals

    def apply_avoid_heavy_exercise(self, biomarkers):
        """
        Avoid Very Heavy Exercise Before Testing:
        May lower ALP by ~10–15% if it was elevated from bone isoenzyme.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        # If ALP > 100 => drop ~15%
        if alp > 100:
            new_vals["alkaline_phosphatase"] = max(alp * 0.85, 50)
        else:
            # small drop
            new_vals["alkaline_phosphatase"] = max(alp - 5, 30)
        return new_vals

    def apply_milk_thistle(self, biomarkers):
        """
        Milk Thistle (1 g/day):
        Reduces ALP by 20–40 U/L if elevated.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        if alp >= 130:
            new_vals["alkaline_phosphatase"] = max(alp - 30, 50)
        elif alp >= 100:
            new_vals["alkaline_phosphatase"] = max(alp - 20, 50)
        return new_vals

    def apply_nac(self, biomarkers):
        """
        NAC (1–2 g/day):
        Might lower ALP by 5–15% if elevated.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        if alp >= 120:
            new_vals["alkaline_phosphatase"] = max(alp * 0.85, 50)
        elif alp >= 100:
            new_vals["alkaline_phosphatase"] = max(alp * 0.90, 50)
        return new_vals

    def apply_carb_fat_restriction(self, biomarkers):
        """
        Carb & Fat Restriction => 5–20 mg/dL glucose reduction if baseline is high
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = self.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = self.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = self.clamp(glu - 3, 70)
        return new_vals

    def apply_postmeal_walk(self, biomarkers):
        """
        Walking After Meals => small effect on fasting glucose (maybe 2–5 mg/dL)
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu > 100:
            new_vals["glucose"] = self.clamp(glu - 5, 70)
        else:
            new_vals["glucose"] = self.clamp(glu - 2, 70)
        return new_vals

    def apply_sauna(self, biomarkers):
        """
        Sauna => mild lowering of glucose (2–5 mg/dL), 
                 raises WBC & lymphocyte% short term, can help if low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        # Glucose
        glu = new_vals["glucose"]
        new_vals["glucose"] = self.clamp(glu - 4, 70)

        # WBC: if low, might raise; if normal/high, no big change
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.5  # mild bump
        # Lymphocyte: if <30, might raise it
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = self.clamp(lymph + 5, 5, 60)
        return new_vals

    def apply_berberine(self, biomarkers):
        """
        Berberine (500–1000 mg/day):
        Lowers glucose by ~10–20 mg/dL if diabetic, smaller if borderline
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = self.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = self.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = self.clamp(glu - 3, 70)
        return new_vals

    def apply_vitb1(self, biomarkers):
        """
        Vitamin B1 (Thiamine ~100 mg/day):
        If user is borderline high glucose, might drop ~5 mg/dL
        If truly high, maybe 10 mg/dL
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = self.clamp(glu - 10, 70)
        elif glu >= 100:
            new_vals["glucose"] = self.clamp(glu - 5, 70)
        return new_vals

    def apply_olive_oil(self, biomarkers):
        """
        Olive Oil (Mediterranean):
        Slightly lowers neutrophils => raises lymph% a bit if was low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        lymph = new_vals["lymphocyte"]
        if lymph < 35:
            new_vals["lymphocyte"] = self.clamp(lymph + 3, 5, 60)
        return new_vals

    def apply_mushrooms(self, biomarkers):
        """
        Mushrooms: can raise lymphocyte% by up to ~5–10 points if low
        Also can raise WBC if low.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        lymph = new_vals["lymphocyte"]
        if lymph < 35:
            new_vals["lymphocyte"] = self.clamp(lymph + 7, 5, 60)
        
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.8
        return new_vals

    def apply_zinc(self, biomarkers):
        """
        Zinc: If user has low lymphocytes or WBC, can raise them somewhat
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.5
        
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = self.clamp(lymph + 5, 5, 60)
        return new_vals

    def apply_bcomplex(self, biomarkers):
        """
        B-Complex: can fix elevated RDW from B12/folate deficiency,
        and can fix high MCV if macrocytic.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        rdw = new_vals["rdw"]
        if rdw >= 18.0:
            # big drop to normal
            new_vals["rdw"] = 14.0
        elif rdw >= 15.0:
            new_vals["rdw"] = 13.5
        
        mcv = new_vals["mcv"]
        if mcv >= 100:
            new_vals["mcv"] = max(mcv - 10, 80)  # drop ~10 fL
        return new_vals

    def apply_balanced_diet(self, biomarkers):
        """
        Well-Balanced Diet: helps albumin if malnourished, helps MCV if micro/macro,
        small CRP improvement, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        # albumin
        alb = new_vals["albumin"]
        if alb < 4.0:
            new_vals["albumin"] = min(alb + 0.5, 5.0)
        
        # MCV: if out of range, nudge toward normal
        mcv = new_vals["mcv"]
        if mcv < 80:
            new_vals["mcv"] = min(mcv + 5, 80)
        elif mcv > 100:
            new_vals["mcv"] = max(mcv - 5, 100)
        
        # CRP small improvement
        crp = new_vals["crp"]
        new_vals["crp"] = self.clamp(crp - 0.3, 0.01)
        
        return new_vals

    def get_interventions(self):
        """
        Return a list of interventions and the corresponding apply functions
        
        Returns:
        --------
        list
            List of dictionaries containing intervention names and their apply functions
        """
        return [
            {"name": "Regular Exercise", "apply_fn": self.apply_exercise},
            {"name": "Weight Loss", "apply_fn": self.apply_weight_loss},
            {"name": "Low Allergen Diet", "apply_fn": self.apply_low_allergen_diet},
            {"name": "Curcumin (500 mg/day)", "apply_fn": self.apply_curcumin},
            {"name": "Omega-3 (1.5–3 g/day)", "apply_fn": self.apply_omega3},
            {"name": "Taurine (3–6 g/day)", "apply_fn": self.apply_taurine},
            {"name": "High Protein Intake", "apply_fn": self.apply_high_protein_diet},
            {"name": "Well-Balanced Diet", "apply_fn": self.apply_balanced_diet},
            {"name": "Reduce Alcohol", "apply_fn": self.apply_reduce_alcohol},
            {"name": "Stop Creatine Supplementation", "apply_fn": self.apply_stop_creatine},
            {"name": "Reduce Red Meat Intake", "apply_fn": self.apply_reduce_red_meat},
            {"name": "Reduce Sodium", "apply_fn": self.apply_reduce_sodium},
            {"name": "Avoid NSAIDs", "apply_fn": self.apply_avoid_nsaids},
            {"name": "Avoid Very Heavy Exercise", "apply_fn": self.apply_avoid_heavy_exercise},
            {"name": "Milk Thistle (1 g/day)", "apply_fn": self.apply_milk_thistle},
            {"name": "NAC (1–2 g/day)", "apply_fn": self.apply_nac},
            {"name": "Carb & Fat Restriction", "apply_fn": self.apply_carb_fat_restriction},
            {"name": "Walking After Meals", "apply_fn": self.apply_postmeal_walk},
            {"name": "Sauna", "apply_fn": self.apply_sauna},
            {"name": "Berberine (500–1000 mg/day)", "apply_fn": self.apply_berberine},
            {"name": "Vitamin B1 (100 mg/day)", "apply_fn": self.apply_vitb1},
            {"name": "Olive Oil (Med Diet)", "apply_fn": self.apply_olive_oil},
            {"name": "Mushrooms (Beta-Glucans)", "apply_fn": self.apply_mushrooms},
            {"name": "Zinc Supplementation", "apply_fn": self.apply_zinc},
            {"name": "B-Complex (B12/Folate)", "apply_fn": self.apply_bcomplex}
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
        base_result = self.calculate_phenoage(biomarker_data)
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
            new_res = self.calculate_phenoage(updated)
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
        base_result = self.calculate_phenoage(biomarker_data)
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
        new_res = self.calculate_phenoage(updated)
        new_pheno = new_res["pheno_age"]
        
        return {
            "original_biomarkers": biomarker_data,
            "updated_biomarkers": updated,
            "original_pheno_age": base_pheno,
            "new_pheno_age": new_pheno,
            "delta": new_pheno - base_pheno,
            "applied_interventions": applied_interventions
        }


def create_example_tsv():
    """Create an example TSV file with biomarker data."""
    example_data = pd.DataFrame([
        {
            "ID": "SUBJ001",
            "Sex": "M",
            "Collection_Date": "2024-10-15",
            "Albumin": 4.47,
            "Creatinine": 1.17,
            "Glucose": 77,
            "CRP": 0.07,
            "Lymphocyte": 36,
            "MCV": 90,
            "RDW": 13.7,
            "Alkaline_Phosphatase": 54,
            "WBC": 4.5,
            "Chronological_Age": 46
        },
        {
            "ID": "SUBJ002",
            "Sex": "F",
            "Collection_Date": "2024-10-16",
            "Albumin": 4.2,
            "Creatinine": 0.9,
            "Glucose": 85,
            "CRP": 0.12,
            "Lymphocyte": 32,
            "MCV": 88,
            "RDW": 12.9,
            "Alkaline_Phosphatase": 62,
            "WBC": 5.2,
            "Chronological_Age": 39
        }
    ])
    
    example_data.to_csv("example_biomarkers.tsv", sep='\t', index=False)
    print("Created example_biomarkers.tsv with sample data")
    print("\nFile Format Description:")
    print("- Each row represents a different subject")
    print("- Columns contain biomarker values and metadata")
    print("- Required biomarkers for PhenoAge calculation:")
    print("  * Albumin (g/dL)")
    print("  * Creatinine (mg/dL)")
    print("  * Glucose (mg/dL)")
    print("  * CRP (mg/L)")
    print("  * Lymphocyte (%)")
    print("  * MCV (fL)")
    print("  * RDW (%)")
    print("  * Alkaline_Phosphatase (U/L)")
    print(f"  * WBC (10^3 cells/µL)")  # Updated unit
    print("  * Chronological_Age (years)")
    print("- Additional metadata columns are optional")


# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Age Clock Calculator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create example TSV file
    example_parser = subparsers.add_parser("create-example", help="Create an example TSV file")
    
    # Process TSV file
    process_parser = subparsers.add_parser("process", help="Process a TSV file with biomarker data")
    process_parser.add_argument("input_file", help="Path to input TSV file")
    process_parser.add_argument("--output", "-o", help="Path to output file")
    process_parser.add_argument("--format", "-f", choices=["tsv", "csv", "excel", "json"], default="tsv",
                              help="Output file format (default: tsv)")
    process_parser.add_argument("--rank", "-r", action="store_true", 
                             help="Generate intervention rankings for each individual")
    process_parser.add_argument("--apply", "-a", 
                             help="Comma-separated list of interventions to apply to each individual")
    
    # Calculate single set of biomarkers
    calc_parser = subparsers.add_parser("calculate", help="Calculate age clocks for a single set of biomarkers")
    calc_parser.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    calc_parser.add_argument("--creatinine", type=float, required=True, help="Creatinine (mg/dL)")
    calc_parser.add_argument("--glucose", type=float, required=True, help="Glucose (mg/dL)")
    calc_parser.add_argument("--crp", type=float, required=True, help="CRP (mg/L)")
    calc_parser.add_argument("--lymphocyte", type=float, required=True, help="Lymphocyte (%)")
    calc_parser.add_argument("--mcv", type=float, required=True, help="MCV (fL)")
    calc_parser.add_argument("--rdw", type=float, required=True, help="RDW (%)")
    calc_parser.add_argument("--alp", type=float, required=True, help="Alkaline Phosphatase (U/L)")
    calc_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")  # Updated unit
    calc_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    
    # Rank interventions
    rank_parser = subparsers.add_parser("rank", help="Rank interventions by their impact on PhenoAge")
    rank_parser.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    rank_parser.add_argument("--creatinine", type=float, required=True, help="Creatinine (mg/dL)")
    rank_parser.add_argument("--glucose", type=float, required=True, help="Glucose (mg/dL)")
    rank_parser.add_argument("--crp", type=float, required=True, help="CRP (mg/L)")
    rank_parser.add_argument("--lymphocyte", type=float, required=True, help="Lymphocyte (%)")
    rank_parser.add_argument("--mcv", type=float, required=True, help="MCV (fL)")
    rank_parser.add_argument("--rdw", type=float, required=True, help="RDW (%)")
    rank_parser.add_argument("--alp", type=float, required=True, help="Alkaline Phosphatase (U/L)")
    rank_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")  # Updated unit
    rank_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    
    # Simulate combined interventions
    combine_parser = subparsers.add_parser("combine", help="Simulate combined effects of multiple interventions")
    combine_parser.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    combine_parser.add_argument("--creatinine", type=float, required=True, help="Creatinine (mg/dL)")
    combine_parser.add_argument("--glucose", type=float, required=True, help="Glucose (mg/dL)")
    combine_parser.add_argument("--crp", type=float, required=True, help="CRP (mg/L)")
    combine_parser.add_argument("--lymphocyte", type=float, required=True, help="Lymphocyte (%)")
    combine_parser.add_argument("--mcv", type=float, required=True, help="MCV (fL)")
    combine_parser.add_argument("--rdw", type=float, required=True, help="RDW (%)")
    combine_parser.add_argument("--alp", type=float, required=True, help="Alkaline Phosphatase (U/L)")
    combine_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")  # Updated unit
    combine_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    combine_parser.add_argument("--interventions", required=True, help="Comma-separated list of intervention names")
    
    args = parser.parse_args()
    
    # Process commands
    calculator = AgeClockCalculator()
    
    if args.command == "create-example":
        create_example_tsv()
        
    elif args.command == "process":
        try:
            results = calculator.process_tsv_file(
                args.input_file, 
                args.output, 
                args.format,
                generate_rankings=args.rank,
                apply_interventions=args.apply
            )
            if not args.output:
                print(results.to_string())
            else:
                print(f"Results saved to {args.output}")
                
                # Print summary of what was done
                print(f"Processed {len(results)} individuals")
                if args.rank:
                    print("Generated personalized intervention rankings for each individual")
                if args.apply:
                    interventions = args.apply.split(",")
                    print(f"Applied {len(interventions)} interventions to each individual:")
                    for intervention in interventions:
                        print(f"  - {intervention.strip()}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
            
    elif args.command == "calculate":
        try:
            biomarker_data = {
                "albumin": args.albumin,
                "creatinine": args.creatinine,
                "glucose": args.glucose,
                "crp": args.crp,
                "lymphocyte": args.lymphocyte,
                "mcv": args.mcv,
                "rdw": args.rdw,
                "alkaline_phosphatase": args.alp,
                "wbc": args.wbc,
                "chronological_age": args.age
            }
            
            # Use the process_direct_input method to demonstrate its usage
            results = calculator.process_direct_input(biomarker_data)[0]
            
            # Print results in a formatted way
            print("\nResults:")
            print(f"  Linear Combination: {results['phenoage_lin_comb']:.4f}")
            print(f"  Mortality Score: {results['phenoage_mort_score']:.4f}")
            print(f"  PhenoAge: {results['phenoage_pheno_age']:.4f} years")
            print(f"  Estimated DNAm Age: {results['phenoage_est_dnam_age']:.4f} years")
            print(f"  Estimated D MScore: {results['phenoage_est_d_mscore']:.4f}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "rank":
        try:
            biomarker_data = {
                "albumin": args.albumin,
                "creatinine": args.creatinine,
                "glucose": args.glucose,
                "crp": args.crp,
                "lymphocyte": args.lymphocyte,
                "mcv": args.mcv,
                "rdw": args.rdw,
                "alkaline_phosphatase": args.alp,
                "wbc": args.wbc,
                "chronological_age": args.age
            }
            
            # Rank interventions
            ranking = calculator.rank_interventions(biomarker_data)
            base_pheno = calculator.calculate_phenoage(biomarker_data)["pheno_age"]
            
            print(f"\nBaseline PhenoAge: {base_pheno:.2f} years")
            print("Interventions ranked by improvement (best first):\n")
            for r in ranking:
                print(f"- {r['intervention']}: new PhenoAge = {r['new_pheno_age']:.2f} years "
                      f"(delta={r['delta']:.2f} years)")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "combine":
        try:
            biomarker_data = {
                "albumin": args.albumin,
                "creatinine": args.creatinine,
                "glucose": args.glucose,
                "crp": args.crp,
                "lymphocyte": args.lymphocyte,
                "mcv": args.mcv,
                "rdw": args.rdw,
                "alkaline_phosphatase": args.alp,
                "wbc": args.wbc,
                "chronological_age": args.age
            }
            
            interventions = [i.strip() for i in args.interventions.split(",")]
            
            # Simulate combined interventions
            result = calculator.simulate_combined_interventions(biomarker_data, interventions)
            
            print("\nCombined Intervention Simulation:")
            print(f"Original PhenoAge: {result['original_pheno_age']:.2f} years")
            print(f"New PhenoAge: {result['new_pheno_age']:.2f} years")
            print(f"Improvement: {-result['delta']:.2f} years")
            print("\nInterventions applied:")
            for i, intervention in enumerate(result['applied_interventions'], 1):
                print(f"  {i}. {intervention}")
            
            print("\nBiomarker Changes:")
            for biomarker in sorted(result['original_biomarkers'].keys()):
                orig = result['original_biomarkers'][biomarker]
                new = result['updated_biomarkers'][biomarker]
                if orig != new:
                    print(f"  {biomarker}: {orig:.2f} → {new:.2f}")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    else:
        # Print examples of usage
        print("Age Clock Calculator - Extended with Intervention Ranking")
        print("\nExamples:")
        print("1. Create example TSV file:")
        print("   python age_clock_calculator.py create-example")
        print("")
        print("2. Process a TSV file:")
        print("   python age_clock_calculator.py process example_biomarkers.tsv -o results.tsv")
        print("")
        print("3. Calculate for a single set of biomarkers:")
        print("   python age_clock_calculator.py calculate --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30")
        print("")
        print("4. Rank interventions by impact on PhenoAge:")
        print("   python age_clock_calculator.py rank --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30")
        print("")
        print("5. Simulate combined interventions:")
        print('   python age_clock_calculator.py combine --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30 --interventions "Regular Exercise,Omega-3 (1.5–3 g/day)"')
        parser.print_help()
