#!/usr/bin/env python3
"""
Command line interface for the PhenoAge Toolkit.

This provides a unified CLI for calculating phenotypic age, percentiles,
ranking interventions, and simulating intervention effects.
"""

import argparse
import sys
import json
import os
import pandas as pd
from .api import PhenoAgeAPI


def create_example_tsv():
    """Create an example TSV file with biomarker data."""
    example_data = pd.DataFrame([
        {
            "ID": "SUBJ001",
            "Sex": "M",
            "Collection_Date": "2024-10-15",
            "albumin": 4.47,
            "creatinine": 1.17,
            "glucose": 77,
            "crp": 0.07,
            "lymphocyte": 36,
            "mcv": 90,
            "rdw": 13.7,
            "alkaline_phosphatase": 54,
            "wbc": 4.5,
            "chronological_age": 46
        },
        {
            "ID": "SUBJ002",
            "Sex": "F",
            "Collection_Date": "2024-10-16",
            "albumin": 4.2,
            "creatinine": 0.9,
            "glucose": 85,
            "crp": 0.12,
            "lymphocyte": 32,
            "mcv": 88,
            "rdw": 12.9,
            "alkaline_phosphatase": 62,
            "wbc": 5.2,
            "chronological_age": 39
        }
    ])
    
    example_data.to_csv("example_biomarkers.tsv", sep='\t', index=False)
    print("Created example_biomarkers.tsv with sample data")
    print("\nFile Format Description:")
    print("- Each row represents a different subject")
    print("- Columns contain biomarker values and metadata")
    print("- Required biomarkers for PhenoAge calculation:")
    print("  * albumin (g/dL)")
    print("  * creatinine (mg/dL)")
    print("  * glucose (mg/dL)")
    print("  * crp (mg/L)")
    print("  * lymphocyte (%)")
    print("  * mcv (fL)")
    print("  * rdw (%)")
    print("  * alkaline_phosphatase (U/L)")
    print(f"  * wbc (10^3 cells/µL)")
    print("  * chronological_age (years)")
    print("- Additional metadata columns are optional")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="PhenoAge Toolkit - Biological Age Calculator and Intervention Simulator")
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
    calc_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")
    calc_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    
    # Calculate percentile
    percentile_parser = subparsers.add_parser("percentile", help="Calculate percentile for phenotypic age")
    percentile_parser.add_argument("--age", type=float, required=True, help="Chronological age in years")
    percentile_parser.add_argument("--phenoage", type=float, required=True, help="Phenotypic age in years")
    
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
    rank_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")
    rank_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    
    # Simulate combined interventions
    combine_parser = subparsers.add_parser("simulate", help="Simulate combined effects of multiple interventions")
    combine_parser.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    combine_parser.add_argument("--creatinine", type=float, required=True, help="Creatinine (mg/dL)")
    combine_parser.add_argument("--glucose", type=float, required=True, help="Glucose (mg/dL)")
    combine_parser.add_argument("--crp", type=float, required=True, help="CRP (mg/L)")
    combine_parser.add_argument("--lymphocyte", type=float, required=True, help="Lymphocyte (%)")
    combine_parser.add_argument("--mcv", type=float, required=True, help="MCV (fL)")
    combine_parser.add_argument("--rdw", type=float, required=True, help="RDW (%)")
    combine_parser.add_argument("--alp", type=float, required=True, help="Alkaline Phosphatase (U/L)")
    combine_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")
    combine_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    combine_parser.add_argument("--interventions", required=True, help="Comma-separated list of intervention names")
    
    # Complete assessment in single command
    assess_parser = subparsers.add_parser("assess", help="Get complete assessment with phenotypic age, percentile, and interventions")
    assess_parser.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    assess_parser.add_argument("--creatinine", type=float, required=True, help="Creatinine (mg/dL)")
    assess_parser.add_argument("--glucose", type=float, required=True, help="Glucose (mg/dL)")
    assess_parser.add_argument("--crp", type=float, required=True, help="CRP (mg/L)")
    assess_parser.add_argument("--lymphocyte", type=float, required=True, help="Lymphocyte (%)")
    assess_parser.add_argument("--mcv", type=float, required=True, help="MCV (fL)")
    assess_parser.add_argument("--rdw", type=float, required=True, help="RDW (%)")
    assess_parser.add_argument("--alp", type=float, required=True, help="Alkaline Phosphatase (U/L)")
    assess_parser.add_argument("--wbc", type=float, required=True, help="WBC (10^3 cells/µL)")
    assess_parser.add_argument("--age", type=float, required=True, help="Chronological Age (years)")
    assess_parser.add_argument("--output", "-o", help="Path to output file (JSON format)")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode (prompt for input)")
    
    args = parser.parse_args()
    
    # Initialize the API
    api = PhenoAgeAPI()
    
    # Process commands
    if args.command == "create-example":
        create_example_tsv()
        
    elif args.command == "process":
        try:
            # Initialize calculator
            calculator = api.calculator
            
            # Process the TSV file
            results_df = calculator.process_tsv_file(args.input_file, None, args.format)
            
            # If rankings requested, generate for each individual
            if args.rank:
                print(f"Generating intervention rankings for {len(results_df)} individuals...")
                for i, row in results_df.iterrows():
                    # Skip rows with errors
                    if 'error' in row and not pd.isna(row['error']):
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
                        rankings = api.rank_interventions(biomarkers)[:5]
                        for j, rank in enumerate(rankings):
                            results_df.at[i, f"rank{j+1}_intervention"] = rank["intervention"]
                            results_df.at[i, f"rank{j+1}_impact"] = -rank["delta"]  # Convert to positive number
                    except Exception as e:
                        results_df.at[i, "ranking_error"] = str(e)
            
            # If specific interventions should be applied
            if args.apply:
                print(f"Applying interventions to {len(results_df)} individuals...")
                intervention_list = [i.strip() for i in args.apply.split(",")]
                
                for i, row in results_df.iterrows():
                    # Skip rows with errors
                    if 'error' in row and not pd.isna(row['error']):
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
                        combined = api.simulate_interventions(biomarkers, intervention_list)
                        
                        # Add results
                        results_df.at[i, "combined_pheno_age"] = combined["new_pheno_age"]
                        results_df.at[i, "years_younger"] = -combined["delta"]
                        results_df.at[i, "original_percentile"] = combined["original_percentile"]
                        results_df.at[i, "new_percentile"] = combined["new_percentile"]
                        results_df.at[i, "percentile_change"] = combined["percentile_change"]
                        
                        # Add biomarker changes 
                        for change in combined["biomarker_changes"]:
                            biomarker = change["biomarker"]
                            new_val = change["new_value"]
                            change_val = change["change"]
                            results_df.at[i, f"{biomarker}_new"] = new_val
                            results_df.at[i, f"{biomarker}_change"] = change_val
                    except Exception as e:
                        results_df.at[i, "intervention_error"] = str(e)
            
            # Save to file if output_path is provided
            if args.output:
                directory = os.path.dirname(args.output)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    
                if args.format.lower() == 'tsv':
                    results_df.to_csv(args.output, sep='\t', index=False)
                elif args.format.lower() == 'csv':
                    results_df.to_csv(args.output, index=False)
                elif args.format.lower() == 'excel':
                    results_df.to_excel(args.output, index=False)
                elif args.format.lower() == 'json':
                    # Convert DataFrame to list of dictionaries
                    results_json = results_df.to_dict(orient='records')
                    with open(args.output, 'w') as f:
                        json.dump(results_json, f, indent=2)
                else:
                    raise ValueError(f"Unsupported output format: {args.format}")
                    
                print(f"Results saved to {args.output}")
            else:
                # Print summary to console
                print(results_df.to_string())
                
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
            
            # Calculate phenotypic age
            results = api.calculate_phenoage(biomarker_data)
            
            # Print results in a formatted way
            print("\nPhenoAge Calculation Results:")
            print(f"  Linear Combination: {results['lin_comb']:.4f}")
            print(f"  Mortality Score: {results['mort_score']:.4f}")
            print(f"  PhenoAge: {results['pheno_age']:.4f} years")
            print(f"  Estimated DNAm Age: {results['est_dnam_age']:.4f} years")
            print(f"  Estimated D MScore: {results['est_d_mscore']:.4f}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "percentile":
        try:
            # Calculate percentile
            percentile = api.calculate_percentile(args.age, args.phenoage)
            
            # Get interpretation
            interpretation = api.interpret_percentile(percentile)
            
            # Get reference values
            references = api.get_reference_values(args.age)
            
            # Calculate age difference
            age_diff = args.age - args.phenoage
            if age_diff > 0:
                age_diff_text = f"{age_diff:.1f} years YOUNGER than your actual age"
            elif age_diff < 0:
                age_diff_text = f"{abs(age_diff):.1f} years OLDER than your actual age"
            else:
                age_diff_text = "exactly matching your chronological age"
            
            # Display results
            print("\n===== PHENOTYPIC AGE ASSESSMENT =====")
            print(f"Chronological Age: {args.age:.1f} years")
            print(f"Phenotypic Age: {args.phenoage:.1f} years")
            print(f"\nYour biological age is {age_diff_text}")
            print(f"\nYou are in the {percentile:.1f}th percentile")
            print(f"This means: {interpretation}")
            
            print("\n--- Reference Values for Your Age ---")
            print(f"10th percentile (less healthy than 90% of people): {references['10th']:.1f} years")
            print(f"25th percentile (less healthy than 75% of people): {references['25th']:.1f} years")
            print(f"50th percentile (median): {references['50th']:.1f} years")
            print(f"75th percentile (healthier than 75% of people): {references['75th']:.1f} years")
            print(f"90th percentile (healthier than 90% of people): {references['90th']:.1f} years")
            
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
            ranking = api.rank_interventions(biomarker_data)
            pheno_age = api.calculate_phenoage(biomarker_data)["pheno_age"]
            percentile = api.calculate_percentile(args.age, pheno_age)
            
            print(f"\nBaseline PhenoAge: {pheno_age:.2f} years (Percentile: {percentile:.2f})")
            print("Interventions ranked by improvement (best first):\n")
            for r in ranking:
                new_percentile = api.calculate_percentile(args.age, r["new_pheno_age"])
                print(f"- {r['intervention']}: new PhenoAge = {r['new_pheno_age']:.2f} years "
                      f"(delta={r['delta']:.2f} years, new percentile: {new_percentile:.2f})")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "simulate":
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
            result = api.simulate_interventions(biomarker_data, interventions)
            
            print("\nCombined Intervention Simulation:")
            print(f"Original PhenoAge: {result['original_pheno_age']:.2f} years")
            print(f"New PhenoAge: {result['new_pheno_age']:.2f} years")
            print(f"Improvement: {-result['delta']:.2f} years")
            
            print(f"\nPercentile Assessment:")
            print(f"Original Percentile: {result['original_percentile']:.2f}")
            print(f"New Percentile: {result['new_percentile']:.2f}")
            print(f"Percentile Improvement: {result['percentile_change']:.2f}")
            print(f"Original Interpretation: {result['original_interpretation']}")
            print(f"New Interpretation: {result['new_interpretation']}")
            
            print("\nInterventions applied:")
            for i, intervention in enumerate(result['applied_interventions'], 1):
                print(f"  {i}. {intervention}")
            
            print("\nBiomarker Changes:")
            for change in result['biomarker_changes']:
                biomarker = change['biomarker']
                orig = change['original_value']
                new = change['new_value']
                change_val = change['change']
                print(f"  {biomarker}: {orig:.2f} → {new:.2f} (change: {change_val:+.2f})")
        
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "assess":
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
            
            # Get complete assessment
            assessment = api.get_complete_assessment(biomarker_data)
            
            # Print the assessment
            print("\n===== PHENOTYPIC AGE ASSESSMENT =====")
            print(f"Chronological Age: {assessment['chronological_age']:.1f} years")
            print(f"Phenotypic Age: {assessment['phenotypic_age']:.1f} years")
            print(f"Percentile: {assessment['percentile']:.1f}")
            print(f"Interpretation: {assessment['interpretation']}")
            print(f"Age Difference: {assessment['age_difference_text']}")
            
            print("\n===== INTERVENTION RECOMMENDATIONS =====")
            print("Top 5 interventions ranked by potential impact:")
            for i, recommendation in enumerate(assessment['intervention_rankings'][:5], 1):
                improvement = -recommendation['delta']
                print(f"{i}. {recommendation['intervention']}: {improvement:.2f} years younger")
            
            # Save to file if requested
            if args.output:
                # Create directory if it doesn't exist
                directory = os.path.dirname(args.output)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                # Save the assessment as JSON
                with open(args.output, 'w') as f:
                    json.dump(assessment, f, indent=2)
                print(f"\nComplete assessment saved to {args.output}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == "interactive":
        try:
            print("\n===== PHENOTYPIC AGE CALCULATOR =====")
            print("This tool calculates your biological age and provides personalized recommendations")
            
            # Get biomarker inputs
            print("\nPlease enter your biomarker values:")
            albumin = float(input("Albumin (g/dL): "))
            creatinine = float(input("Creatinine (mg/dL): "))
            glucose = float(input("Glucose (mg/dL): "))
            crp = float(input("CRP (mg/L): "))
            lymphocyte = float(input("Lymphocyte percentage (%): "))
            mcv = float(input("Mean Cell Volume (fL): "))
            rdw = float(input("Red Cell Distribution Width (%): "))
            alp = float(input("Alkaline Phosphatase (U/L): "))
            wbc = float(input("White Blood Cell count (10^3 cells/µL): "))
            age = float(input("Chronological Age (years): "))
            
            biomarker_data = {
                "albumin": albumin,
                "creatinine": creatinine,
                "glucose": glucose,
                "crp": crp,
                "lymphocyte": lymphocyte,
                "mcv": mcv,
                "rdw": rdw,
                "alkaline_phosphatase": alp,
                "wbc": wbc,
                "chronological_age": age
            }
            
            # Get assessment
            assessment = api.get_bioage_assessment(biomarker_data)
            
            # Display results
            print("\n===== PHENOTYPIC AGE ASSESSMENT =====")
            print(f"Chronological Age: {assessment['chronological_age']:.1f} years")
            print(f"Phenotypic Age: {assessment['phenotypic_age']:.1f} years")
            print(f"\nYour biological age is {assessment['age_difference_text']}")
            print(f"\nYou are in the {assessment['percentile']:.1f}th percentile")
            print(f"This means: {assessment['interpretation']}")
            
            print("\n--- Reference Values for Your Age ---")
            ref = assessment['reference_values']
            print(f"10th percentile (less healthy than 90% of people): {ref['10th']:.1f} years")
            print(f"25th percentile (less healthy than 75% of people): {ref['25th']:.1f} years")
            print(f"50th percentile (median): {ref['50th']:.1f} years")
            print(f"75th percentile (healthier than 75% of people): {ref['75th']:.1f} years")
            print(f"90th percentile (healthier than 90% of people): {ref['90th']:.1f} years")
            
            # Show intervention rankings
            print("\n===== RECOMMENDED INTERVENTIONS =====")
            rankings = api.rank_interventions(biomarker_data)
            print("Interventions ranked by potential impact on biological age:\n")
            for i, r in enumerate(rankings[:10], 1):
                improvement = -r['delta']
                print(f"{i}. {r['intervention']}: {improvement:.2f} years improvement")
            
            # Ask if user wants to simulate interventions
            print("\nWould you like to simulate the effects of selected interventions? (y/n)")
            choice = input().strip().lower()
            
            if choice == 'y' or choice == 'yes':
                print("\nEnter the intervention numbers you wish to simulate (comma-separated, e.g., 1,3,5):")
                selection = input().strip()
                
                try:
                    # Parse selection
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected_interventions = [rankings[i]['intervention'] for i in indices if 0 <= i < len(rankings)]
                    
                    if not selected_interventions:
                        print("No valid interventions selected.")
                    else:
                        # Simulate selected interventions
                        print(f"\nSimulating effects of {len(selected_interventions)} interventions...")
                        result = api.simulate_interventions(biomarker_data, selected_interventions)
                        
                        print("\n===== INTERVENTION SIMULATION RESULTS =====")
                        print(f"Original PhenoAge: {result['original_pheno_age']:.2f} years")
                        print(f"New PhenoAge: {result['new_pheno_age']:.2f} years")
                        print(f"Improvement: {-result['delta']:.2f} years")
                        
                        print(f"\nPercentile Assessment:")
                        print(f"Original Percentile: {result['original_percentile']:.2f}")
                        print(f"New Percentile: {result['new_percentile']:.2f}")
                        print(f"Percentile Improvement: {result['percentile_change']:.2f}")
                        print(f"Original Interpretation: {result['original_interpretation']}")
                        print(f"New Interpretation: {result['new_interpretation']}")
                        
                        print("\nInterventions applied:")
                        for i, intervention in enumerate(result['applied_interventions'], 1):
                            print(f"  {i}. {intervention}")
                        
                        print("\nBiomarker Changes:")
                        for change in result['biomarker_changes']:
                            biomarker = change['biomarker']
                            orig = change['original_value']
                            new = change['new_value']
                            change_val = change['change']
                            print(f"  {biomarker}: {orig:.2f} → {new:.2f} (change: {change_val:+.2f})")
                
                except Exception as e:
                    print(f"Error simulating interventions: {str(e)}")
            
            print("\nThank you for using the PhenoAge Toolkit!")
            
        except ValueError:
            print("Error: Please enter numeric values for all biomarkers.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    else:
        # Print examples of usage
        parser.print_help()
        print("\nExamples:")
        print("1. Create example TSV file:")
        print("   phenoage create-example")
        print("")
        print("2. Process a TSV file:")
        print("   phenoage process example_biomarkers.tsv -o results.tsv")
        print("")
        print("3. Get complete assessment for a single person:")
        print("   phenoage assess --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30")
        print("")
        print("4. Calculate percentile for a known phenotypic age:")
        print("   phenoage percentile --age 45 --phenoage 40")
        print("")
        print("5. Rank interventions by impact:")
        print("   phenoage rank --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30")
        print("")
        print("6. Simulate combined interventions:")
        print('   phenoage simulate --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30 --interventions "Regular Exercise,Omega-3 (1.5–3 g/day)"')
        print("")
        print("7. Run in interactive mode:")
        print("   phenoage interactive")


if __name__ == "__main__":
    main()
