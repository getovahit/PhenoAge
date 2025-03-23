"""
Example usage of the PhenoAge Toolkit demonstrating core functionality.
"""

from phenoage_toolkit import PhenoAgeAPI

# Initialize API
api = PhenoAgeAPI()

# ========= TEST 1: BASIC CALCULATION =========
print("===== TEST 1: BASIC PHENOAGE CALCULATION =====")

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
pheno_results = api.calculate_phenoage(biomarker_data)
print(f"Chronological Age: {biomarker_data['chronological_age']} years")
print(f"Phenotypic Age: {pheno_results['pheno_age']:.2f} years")
print(f"Mortality Score: {pheno_results['mort_score']:.4f}")
print(f"DNAm Age Estimate: {pheno_results['est_dnam_age']:.2f} years")

# ========= TEST 2: PERCENTILE CALCULATION =========
print("\n===== TEST 2: PERCENTILE CALCULATION =====")

chron_age = biomarker_data["chronological_age"]
pheno_age = pheno_results["pheno_age"]

# Calculate percentile
percentile = api.calculate_percentile(chron_age, pheno_age)
interpretation = api.interpret_percentile(percentile)
references = api.get_reference_values(chron_age)

print(f"Chronological Age: {chron_age} years")
print(f"Phenotypic Age: {pheno_age:.2f} years")
print(f"Percentile: {percentile:.2f}")
print(f"Interpretation: {interpretation}")
print("\nReference Values:")
for ref, value in references.items():
    print(f"  {ref} percentile: {value:.2f} years")

# ========= TEST 3: INTERVENTION RANKINGS =========
print("\n===== TEST 3: INTERVENTION RANKINGS =====")

# Get ranked interventions
rankings = api.rank_interventions(biomarker_data)

print(f"Baseline PhenoAge: {pheno_age:.2f} years")
print("Top 5 interventions by impact:")
for i, rank in enumerate(rankings[:5], 1):
    improvement = -rank["delta"]
    print(f"{i}. {rank['intervention']}: {improvement:.2f} years younger")

# ========= TEST 4: INTERVENTION SIMULATION =========
print("\n===== TEST 4: INTERVENTION SIMULATION =====")

# Select top 3 interventions
selected_interventions = [
    rankings[0]["intervention"],
    rankings[1]["intervention"],
    rankings[2]["intervention"]
]

print(f"Selected interventions: {', '.join(selected_interventions)}")

# Simulate combined effects
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

# ========= TEST 5: COMPLETE ASSESSMENT =========
print("\n===== TEST 5: COMPLETE ASSESSMENT =====")

# Get complete assessment
assessment = api.get_complete_assessment(biomarker_data)

print(f"Chronological Age: {assessment['chronological_age']} years")
print(f"Phenotypic Age: {assessment['phenotypic_age']:.2f} years")
print(f"Percentile: {assessment['percentile']:.2f}")
print(f"Interpretation: {assessment['interpretation']}")
print(f"Age Difference: {assessment['age_difference_text']}")

print("\nTop 3 Recommendations:")
for i, rec in enumerate(assessment['intervention_rankings'][:3], 1):
    improvement = -rec['delta']
    print(f"{i}. {rec['intervention']}: {improvement:.2f} years younger")
