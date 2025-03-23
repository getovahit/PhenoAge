"""
Advanced usage examples of the PhenoAge Toolkit demonstrating direct access to components.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from phenoage_toolkit.biomarkers.calculator import AgeClockCalculator
from phenoage_toolkit.percentile.calculator import calculate_percentile, get_reference_values
from phenoage_toolkit.interventions.models import InterventionModels
from phenoage_toolkit.interventions.manager import InterventionManager

# ========= EXAMPLE 1: CUSTOM BIOMARKER ANALYSIS =========
print("===== EXAMPLE 1: CUSTOM BIOMARKER ANALYSIS =====")

# Initialize components directly
calculator = AgeClockCalculator()

# Sample data for multiple subjects
subjects_data = [
    {
        "id": "Subject1",
        "albumin": 4.5, "creatinine": 0.8, "glucose": 80, "crp": 0.2,
        "lymphocyte": 35, "mcv": 90, "rdw": 13.0, "alkaline_phosphatase": 60,
        "wbc": 5.0, "chronological_age": 35
    },
    {
        "id": "Subject2",
        "albumin": 4.2, "creatinine": 0.9, "glucose": 95, "crp": 0.8,
        "lymphocyte": 30, "mcv": 92, "rdw": 14.0, "alkaline_phosphatase": 70,
        "wbc": 5.5, "chronological_age": 40
    },
    {
        "id": "Subject3",
        "albumin": 3.9, "creatinine": 1.1, "glucose": 105, "crp": 1.5,
        "lymphocyte": 28, "mcv": 94, "rdw": 15.0, "alkaline_phosphatase": 80,
        "wbc": 6.0, "chronological_age": 45
    }
]

# Process each subject
results = []
for subject in subjects_data:
    # Calculate phenoage
    pheno_result = calculator.calculate_phenoage(subject)
    
    # Calculate percentile
    percentile = calculate_percentile(
        subject["chronological_age"], 
        pheno_result["pheno_age"]
    )
    
    # Store results
    results.append({
        "id": subject["id"],
        "chronological_age": subject["chronological_age"],
        "phenotypic_age": pheno_result["pheno_age"],
        "percentile": percentile,
        "biological_delta": subject["chronological_age"] - pheno_result["pheno_age"]
    })

# Convert to DataFrame
results_df = pd.DataFrame(results)
print(results_df)

# ========= EXAMPLE 2: CUSTOM INTERVENTION ANALYSIS =========
print("\n===== EXAMPLE 2: CUSTOM INTERVENTION ANALYSIS =====")

# Create intervention manager
intervention_manager = InterventionManager(calculator)

# Sample subject
sample_subject = subjects_data[2]  # Subject with highest glucose, CRP
print(f"Analyzing subject: {sample_subject['id']}")
print(f"Chronological age: {sample_subject['chronological_age']} years")
print(f"Glucose: {sample_subject['glucose']} mg/dL")
print(f"CRP: {sample_subject['crp']} mg/L")

# Apply specific interventions directly
print("\nTesting individual interventions:")

# Test exercise effect
post_exercise = InterventionModels.apply_exercise(sample_subject)
print("\nAfter Exercise:")
print(f"Glucose: {post_exercise['glucose']} mg/dL (-{sample_subject['glucose'] - post_exercise['glucose']})")
print(f"CRP: {post_exercise['crp']} mg/L (-{sample_subject['crp'] - post_exercise['crp']})")

# Test berberine effect
post_berberine = InterventionModels.apply_berberine(sample_subject)
print("\nAfter Berberine:")
print(f"Glucose: {post_berberine['glucose']} mg/dL (-{sample_subject['glucose'] - post_berberine['glucose']})")

# Test curcumin effect
post_curcumin = InterventionModels.apply_curcumin(sample_subject)
print("\nAfter Curcumin:")
print(f"CRP: {post_curcumin['crp']} mg/L (-{sample_subject['crp'] - post_curcumin['crp']})")

# ========= EXAMPLE 3: CUSTOM COMPARISON ANALYSIS =========
print("\n===== EXAMPLE 3: CUSTOM PERCENTILE COMPARISON =====")

# Get baseline phenotypic age
baseline_pheno = calculator.calculate_phenoage(sample_subject)["pheno_age"]
print(f"Baseline phenotypic age: {baseline_pheno:.2f} years")

# Get reference values for age peers
references = get_reference_values(sample_subject["chronological_age"])
print("\nPercentile reference values for age peers:")
for percentile, value in references.items():
    print(f"{percentile} percentile: {value:.2f} years")

# Calculate baseline percentile
baseline_percentile = calculate_percentile(
    sample_subject["chronological_age"], 
    baseline_pheno
)
print(f"\nBaseline percentile: {baseline_percentile:.2f}")

# Simulate improvement to 75th percentile
target_pheno = references["75th"]
improvement_needed = baseline_pheno - target_pheno
print(f"\nTo reach 75th percentile:")
print(f"Current phenotypic age: {baseline_pheno:.2f} years")
print(f"Target phenotypic age: {target_pheno:.2f} years")
print(f"Improvement needed: {improvement_needed:.2f} years")

# ========= EXAMPLE 4: SIMULATE CUSTOM INTERVENTION COMBINATIONS =========
print("\n===== EXAMPLE 4: CUSTOM INTERVENTION COMBINATIONS =====")

# Get all available interventions
all_interventions = intervention_manager.get_interventions()
print(f"Total available interventions: {len(all_interventions)}")

# Create custom combinations to test
combinations = [
    ["Regular Exercise", "Berberine (500–1000 mg/day)"],
    ["Weight Loss", "Reduce Alcohol", "Curcumin (500 mg/day)"],
    ["Omega-3 (1.5–3 g/day)", "Taurine (3–6 g/day)", "B-Complex (B12/Folate)"]
]

# Test each combination
for i, combo in enumerate(combinations, 1):
    print(f"\nCombination {i}: {', '.join(combo)}")
    
    # Simulate
    simulation = intervention_manager.simulate_combined_interventions(
        sample_subject, 
        combo
    )
    
    # Calculate percentiles
    original_percentile = calculate_percentile(
        sample_subject["chronological_age"],
        simulation["original_pheno_age"]
    )
    
    new_percentile = calculate_percentile(
        sample_subject["chronological_age"],
        simulation["new_pheno_age"]
    )
    
    # Print results
    print(f"Original phenotypic age: {simulation['original_pheno_age']:.2f} years")
    print(f"New phenotypic age: {simulation['new_pheno_age']:.2f} years")
    print(f"Improvement: {-simulation['delta']:.2f} years")
    print(f"Original percentile: {original_percentile:.2f}")
    print(f"New percentile: {new_percentile:.2f}")
    print(f"Percentile improvement: {new_percentile - original_percentile:.2f}")
