"""
Test script for PhenoAge Toolkit
"""

from phenoage_toolkit import PhenoAgeAPI

# Initialize API
api = PhenoAgeAPI()

print("===== TESTING PHENOAGE TOOLKIT =====")

# Sample biomarker data
biomarker_data = {
    "albumin": 4.2,                  # g/dL
    "creatinine": 0.9,               # mg/dL
    "glucose": 85,                   # mg/dL
    "crp": 0.5,                      # mg/L
    "lymphocyte": 32,                # %
    "mcv": 88,                       # fL
    "rdw": 12.9,                     # %
    "alkaline_phosphatase": 62,      # U/L
    "wbc": 5.2,                      # 10^3 cells/µL
    "chronological_age": 40          # years
}

# Calculate phenotypic age
print("\n1. Basic PhenoAge Calculation:")
try:
    pheno_results = api.calculate_phenoage(biomarker_data)
    print(f"Chronological Age: {biomarker_data['chronological_age']} years")
    print(f"Phenotypic Age: {pheno_results['pheno_age']:.2f} years")
    print("✓ Basic calculation successful")
except Exception as e:
    print(f"✗ Error in calculation: {e}")

# Calculate percentile
print("\n2. Percentile Calculation:")
try:
    chron_age = biomarker_data["chronological_age"]
    pheno_age = pheno_results["pheno_age"]
    percentile = api.calculate_percentile(chron_age, pheno_age)
    print(f"Percentile: {percentile:.2f}")
    print("✓ Percentile calculation successful")
except Exception as e:
    print(f"✗ Error in percentile calculation: {e}")

# Get intervention rankings
print("\n3. Intervention Rankings:")
try:
    rankings = api.rank_interventions(biomarker_data)
    print("Top 3 interventions by impact:")
    for i, rank in enumerate(rankings[:3], 1):
        improvement = -rank["delta"]
        print(f"{i}. {rank['intervention']}: {improvement:.2f} years younger")
    print("✓ Intervention ranking successful")
except Exception as e:
    print(f"✗ Error in intervention ranking: {e}")

# Simulate interventions
print("\n4. Intervention Simulation:")
try:
    selected_interventions = [
        rankings[0]["intervention"],
        rankings[1]["intervention"]
    ]
    print(f"Selected interventions: {', '.join(selected_interventions)}")
    
    simulation = api.simulate_interventions(biomarker_data, selected_interventions)
    
    print(f"Original PhenoAge: {simulation['original_pheno_age']:.2f} years")
    print(f"New PhenoAge: {simulation['new_pheno_age']:.2f} years")
    print(f"Improvement: {-simulation['delta']:.2f} years")
    print("✓ Intervention simulation successful")
except Exception as e:
    print(f"✗ Error in intervention simulation: {e}")

# Get complete assessment
print("\n5. Complete Assessment:")
try:
    assessment = api.get_complete_assessment(biomarker_data)
    
    print(f"Chronological Age: {assessment['chronological_age']} years")
    print(f"Phenotypic Age: {assessment['phenotypic_age']:.2f} years")
    print(f"Percentile: {assessment['percentile']:.2f}")
    print(f"Interpretation: {assessment['interpretation']}")
    
    print("\nTop 3 Recommendations:")
    for i, rec in enumerate(assessment['intervention_rankings'][:3], 1):
        improvement = -rec['delta']
        print(f"{i}. {rec['intervention']}: {improvement:.2f} years younger")
    
    print("✓ Complete assessment successful")
except Exception as e:
    print(f"✗ Error in complete assessment: {e}")

print("\n===== TEST SUMMARY =====")
print("This test validates the core functionality of the PhenoAge Toolkit.")
print("If all tests passed, the toolkit is working correctly.")