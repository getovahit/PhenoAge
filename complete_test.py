"""
PhenoAge Toolkit Complete Test
"""
from phenoage_toolkit.api import PhenoAgeAPI

# Initialize API
api = PhenoAgeAPI()

print("===== PHENOAGE TOOLKIT COMPLETE TEST =====")

# Test data
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

# 1. Basic PhenoAge Calculation
print("\n1) BASIC PHENOAGE CALCULATION")
pheno_results = api.calculate_phenoage(biomarker_data)
print(f"Chronological Age: {biomarker_data['chronological_age']} years")
print(f"Phenotypic Age: {pheno_results['pheno_age']:.2f} years")
print(f"Mortality Score: {pheno_results.get('mort_score', 'N/A')}")
print(f"DNAm Age Estimate: {pheno_results.get('est_dnam_age', 'N/A')}")

# 2. Percentile Calculation
print("\n2) PERCENTILE CALCULATION")
percentile = api.calculate_percentile(
    biomarker_data["chronological_age"], 
    pheno_results["pheno_age"]
)
interpretation = api.interpret_percentile(percentile)
print(f"Percentile: {percentile:.2f}")
print(f"Interpretation: {interpretation}")

# 3. Intervention Rankings
print("\n3) INTERVENTION RANKINGS")
rankings = api.rank_interventions(biomarker_data)
print("Top 5 interventions by impact:")
for i, rank in enumerate(rankings[:5], 1):
    improvement = -rank["delta"]
    print(f"{i}. {rank['intervention']}: {improvement:.2f} years younger")

# 4. Intervention Simulation
print("\n4) INTERVENTION SIMULATION")
selected_interventions = [
    rankings[0]["intervention"], 
    rankings[1]["intervention"],
    rankings[2]["intervention"]
]
print(f"Selected interventions: {', '.join(selected_interventions)}")

simulation = api.simulate_interventions(biomarker_data, selected_interventions)
print("\nResults:")
print(f"Original PhenoAge: {simulation['original_pheno_age']:.2f} years")
print(f"New PhenoAge: {simulation['new_pheno_age']:.2f} years")
print(f"Improvement: {-simulation['delta']:.2f} years")
print(f"Original Percentile: {simulation['original_percentile']:.2f}")
print(f"New Percentile: {simulation['new_percentile']:.2f}")
print(f"Percentile Improvement: {simulation['percentile_change']:.2f}")

print("\nBiomarker Changes:")
for change in simulation['biomarker_changes']:
    biomarker = change['biomarker']
    orig = change['original_value']
    new = change['new_value']
    change_val = change['change']
    print(f"  {biomarker}: {orig:.2f} → {new:.2f} (change: {change_val:+.2f})")

# 5. Complete Assessment
print("\n5) COMPLETE ASSESSMENT")
assessment = api.get_complete_assessment(biomarker_data)
print(f"Chronological Age: {assessment['chronological_age']} years")
print(f"Phenotypic Age: {assessment['phenotypic_age']:.2f} years")
print(f"Percentile: {assessment['percentile']:.2f}")
print(f"Interpretation: {assessment['interpretation']}")
print(f"Age Difference: {assessment.get('age_difference_text', 'N/A')}")

print("\nTop 3 Recommendations:")
for i, rec in enumerate(assessment['intervention_rankings'][:3], 1):
    improvement = -rec['delta']
    print(f"{i}. {rec['intervention']}: {improvement:.2f} years younger")

print("\n===== TEST COMPLETE =====")