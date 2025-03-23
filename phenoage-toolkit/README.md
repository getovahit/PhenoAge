# PhenoAge Toolkit

A comprehensive Python toolkit for calculating biological age based on biomarkers, determining percentile rankings compared to age peers, and simulating the effects of lifestyle and supplement interventions.

## Overview

The PhenoAge Toolkit provides a modular approach to:

1. Calculate phenotypic age (biological age) from standard clinical biomarkers
2. Determine percentile rankings compared to chronological age peers
3. Rank personalized interventions by their potential to reduce biological age
4. Simulate the combined effects of multiple interventions
5. Quantify before/after improvements in both absolute years and percentile rankings

The toolkit implements the validated PhenoAge algorithm (Levine et al.), converts biomarker units, applies scientifically validated weights, and computes age-related metrics. Additionally, it models the effects of 25 different interventions based on clinical literature.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/phenoage-toolkit.git
cd phenoage-toolkit

# Install the package
pip install .
```

## Required Biomarkers

The following biomarkers are required for PhenoAge calculation:

| Biomarker             | Expected Unit      | Description                    |
|-----------------------|-------------------|--------------------------------|
| Albumin               | g/dL              | Serum albumin level            |
| Creatinine            | mg/dL             | Serum creatinine level         |
| Glucose               | mg/dL             | Fasting blood glucose          |
| CRP                   | mg/L              | C-reactive protein             |
| Lymphocyte            | %                 | Lymphocyte percentage          |
| MCV                   | fL                | Mean corpuscular volume        |
| RDW                   | %                 | Red cell distribution width    |
| Alkaline Phosphatase  | U/L               | Alkaline phosphatase level     |
| WBC                   | 10^3 cells/µL     | White blood cell count         |
| Chronological Age     | years             | Patient's chronological age    |

## Usage

### Python API

#### Basic Usage

```python
from phenoage_toolkit import PhenoAgeAPI

# Initialize the API
api = PhenoAgeAPI()

# Prepare biomarker data
biomarker_data = {
    "albumin": 4.7,                 # g/dL
    "creatinine": 0.8,              # mg/dL
    "glucose": 75.9,                # mg/dL
    "crp": 0.1,                     # mg/L
    "lymphocyte": 57.5,             # %
    "mcv": 92.9,                    # fL
    "rdw": 13.3,                    # %
    "alkaline_phosphatase": 15,     # U/L
    "wbc": 4.1,                     # 10^3 cells/µL
    "chronological_age": 30         # years
}

# Get complete assessment
assessment = api.get_complete_assessment(biomarker_data)

# Access results
print(f"Chronological Age: {assessment['chronological_age']} years")
print(f"Phenotypic Age: {assessment['phenotypic_age']:.2f} years")
print(f"Percentile Rank: {assessment['percentile']:.2f}")
print(f"Interpretation: {assessment['interpretation']}")

# View top intervention recommendations
print("\nTop 3 Recommended Interventions:")
for i, rec in enumerate(assessment['intervention_rankings'][:3], 1):
    print(f"{i}. {rec['intervention']}: {-rec['delta']:.2f} years improvement")
```

#### Simulating Interventions

```python
# Select interventions based on recommendations or user preference
selected_interventions = [
    "Regular Exercise",
    "Omega-3 (1.5–3 g/day)",
    "Curcumin (500 mg/day)"
]

# Simulate the combined effect of these interventions
simulation = api.simulate_interventions(biomarker_data, selected_interventions)

# View results
print(f"Original PhenoAge: {simulation['original_pheno_age']:.2f} years")
print(f"New PhenoAge: {simulation['new_pheno_age']:.2f} years")
print(f"Improvement: {-simulation['delta']:.2f} years")
print(f"Original Percentile: {simulation['original_percentile']:.2f}")
print(f"New Percentile: {simulation['new_percentile']:.2f}")
print(f"Percentile Improvement: {simulation['percentile_change']:.2f}")

# View biomarker changes
print("\nBiomarker Changes:")
for change in simulation['biomarker_changes']:
    print(f"{change['biomarker']}: {change['original_value']:.2f} → {change['new_value']:.2f}")
```

### Command Line Interface

#### Complete Assessment

```bash
phenoage assess --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 \
  --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30
```

#### Calculate Percentile

```bash
phenoage percentile --age 45 --phenoage 40
```

#### Rank Interventions

```bash
phenoage rank --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 \
  --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30
```

#### Simulate Interventions

```bash
phenoage simulate --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 \
  --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30 \
  --interventions "Regular Exercise,Omega-3 (1.5–3 g/day)"
```

#### Process TSV Files with Multiple Subjects

```bash
# Process a file
phenoage process example_biomarkers.tsv --output results.tsv

# Process with intervention rankings
phenoage process example_biomarkers.tsv --output results_with_rankings.tsv --rank

# Process with specific interventions
phenoage process example_biomarkers.tsv --output intervention_results.tsv \
  --apply "Regular Exercise,Omega-3 (1.5–3 g/day)"
```

#### Interactive Mode

```bash
phenoage interactive
```

## Modular Architecture

The PhenoAge Toolkit has a modular design to allow flexible usage:

```
phenoage_toolkit/
├── api.py                  # High-level unified API
├── biomarkers/             # Biomarker calculations
│   └── calculator.py       # PhenoAge calculator
├── percentile/             # Percentile calculations
│   └── calculator.py       # Percentile calculator
├── interventions/          # Intervention simulations
│   ├── models.py           # Intervention effects
│   └── manager.py          # Intervention ranking
└── cli.py                  # Command line interface
```

### Advanced Usage with Individual Modules

```python
# Direct access to biomarker calculations
from phenoage_toolkit.biomarkers.calculator import AgeClockCalculator
calculator = AgeClockCalculator()
pheno_results = calculator.calculate_phenoage(biomarker_data)

# Direct access to percentile calculations
from phenoage_toolkit.percentile.calculator import calculate_percentile
percentile = calculate_percentile(30, 25.5)  # chronological_age, phenotypic_age

# Direct access to intervention models
from phenoage_toolkit.interventions.models import InterventionModels
updated_biomarkers = InterventionModels.apply_exercise(biomarker_data)
```

## Available Interventions

The toolkit includes 25 interventions based on clinical literature:

1. **Regular Exercise**:
   - Reduces CRP (more if elevated)
   - Lowers glucose (5-15 mg/dL)
   - Can reduce WBC if elevated
   - Can increase lymphocyte percentage if low

2. **Weight Loss**:
   - Reduces CRP by 30-40%
   - Lowers glucose by 5-20 mg/dL
   - Can reduce WBC if elevated

3. **Curcumin (500-1000 mg/day)**:
   - Reduces CRP significantly (up to 3.7 mg/L if elevated)

4. **Omega-3 (1.5-3 g/day)**:
   - Reduces CRP
   - Can reduce WBC if elevated
   - May increase albumin in inflammatory states
   - Can increase lymphocyte percentage

5. **Low Allergen / Anti-Inflammatory Diet**:
   - Reduces CRP by 0.2-1.0 mg/L depending on baseline

And 20 more interventions targeting various biomarkers.

## Mathematical Details

### PhenoAge Calculation

The PhenoAge algorithm follows a multi-step process:

1. **Unit Conversion**:
   - Albumin: g/dL → g/L (multiply by 10)
   - Creatinine: mg/dL → μmol/L (multiply by 88.4)
   - Glucose: mg/dL → mmol/L (multiply by 0.0555)
   - CRP: mg/L → ln(mg/dL) (multiply by 0.1 then take natural log)
   
2. **Apply Weights (from Levine et al. 2018)**
3. **Calculate Linear Combination**
4. **Calculate Mortality Score**
5. **Calculate PhenoAge**
6. **Calculate Estimated DNAm Age**
7. **Calculate Estimated D MScore**

### Percentile Calculation

Percentile calculations use a normal distribution approximation:

1. **Calculate Z-score**: 
   ```
   z_score = (phenotypic_age - chronological_age) / 5.5
   ```
   
2. **Convert to Percentile**: 
   ```
   percentile = (1 - norm.cdf(z_score)) * 100
   ```
   
3. **Interpretation**: Higher percentiles indicate a younger biological age relative to chronological age peers.

## Example Output

### Basic Assessment

```
===== PHENOTYPIC AGE ASSESSMENT =====
Chronological Age: 46.0 years
Phenotypic Age: 40.2 years
Percentile: 85.4
Interpretation: Very good - younger biological age than 75% of people your age
Age Difference: 5.8 years YOUNGER than chronological age

===== INTERVENTION RECOMMENDATIONS =====
Top 5 interventions ranked by potential impact:
1. Curcumin (500 mg/day): 1.23 years younger
2. Regular Exercise: 0.98 years younger
3. Omega-3 (1.5–3 g/day): 0.87 years younger
4. Low Allergen Diet: 0.56 years younger
5. Mushrooms (Beta-Glucans): 0.42 years younger
```

### Intervention Simulation

```
Combined Intervention Simulation:
Original PhenoAge: 40.2 years
New PhenoAge: 37.5 years
Improvement: 2.7 years

Percentile Assessment:
Original Percentile: 85.4
New Percentile: 92.1
Percentile Improvement: 6.7
Original Interpretation: Very good - younger biological age than 75% of people your age
New Interpretation: Excellent - younger biological age than 90% of people your age

Interventions applied:
  1. Regular Exercise
  2. Curcumin (500 mg/day)
  3. Omega-3 (1.5–3 g/day)

Biomarker Changes:
  crp: 0.07 → 0.01 (change: -0.06)
  glucose: 77.00 → 74.00 (change: -3.00)
  lymphocyte: 36.00 → 41.00 (change: +5.00)
  albumin: 4.47 → 4.67 (change: +0.20)
```

## Requirements

- Python 3.6+
- NumPy
- Pandas
- SciPy

## License

See [LICENSE](LICENSE) for details. Copyright 2025 Puya Yazdi. All rights reserved.

## Acknowledgments

- PhenoAge calculation based on method by Levine et al. (2018)
- Intervention effects based on systematic review of clinical literature
