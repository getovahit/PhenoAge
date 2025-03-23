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
            "wbc": "10^3 cells/µL",
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

    def process_tsv_file(self, file_path, output_path=None, output_format='tsv'):
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
