# Age Clock Calculator with Intervention Ranking

A comprehensive Python toolkit for calculating biological age clocks based on biomarker data and simulating the effects of lifestyle and supplementation interventions. Currently supports PhenoAge calculation with ranking of 25 evidence-based interventions.

## Overview

The Age Clock Calculator provides a powerful and flexible way to:

1. Calculate biological age based on standard clinical biomarkers
2. Rank personalized interventions by their potential to reduce biological age
3. Simulate the combined effects of multiple interventions
4. Process both individual biomarker sets and large datasets

The calculator implements the validated PhenoAge algorithm, converts biomarker units, applies scientifically validated weights, and computes age-related metrics. Additionally, it models the effects of 25 different interventions based on clinical literature.

## Features

- **PhenoAge Calculation**: Implements the Levine et al. method for phenotypic age estimation
- **Intervention Ranking**: Ranks 25 different interventions by their impact on reducing biological age
- **Intervention Simulation**: Simulates the effects of combining multiple interventions
- **Batch Processing**: Efficiently processes large datasets with thousands of individuals
- **Multiple Output Formats**: Results available as TSV, CSV, Excel, JSON, or Python objects
- **Biomarker Name Aliases**: Recognizes different naming conventions for the same biomarker
- **Error Handling**: Provides informative errors about missing or invalid biomarkers
- **Well-Documented API**: Clear documentation for all methods and parameters

## Installation

```bash
# Clone the repository
git clone https://github.com/getovahit/PhenoAge.git
cd PhenoAge

# Install requirements
pip install -r requirements.txt
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

## Command-Line Usage

### Calculate for a Single Set of Biomarkers

```bash
python age_clock_calculator.py calculate --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30
```

### Rank Interventions for an Individual

```bash
python age_clock_calculator.py rank --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30
```

### Simulate Combined Interventions

```bash
python age_clock_calculator.py combine --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30 --interventions "Regular Exercise,Omega-3 (1.5–3 g/day)"
```

### Process a TSV File (Basic)

```bash
python age_clock_calculator.py process example_biomarkers.tsv --output results.tsv
```

### Process a TSV File with Intervention Rankings

```bash
python age_clock_calculator.py process example_biomarkers.tsv --output results_with_rankings.tsv --rank
```

### Process a TSV File with Specific Interventions

```bash
python age_clock_calculator.py process example_biomarkers.tsv --output intervention_results.tsv --apply "Regular Exercise,Omega-3 (1.5–3 g/day)"
```

### Process a TSV File with Both Rankings and Interventions

```bash
python age_clock_calculator.py process example_biomarkers.tsv --output full_results.tsv --rank --apply "Regular Exercise,Omega-3 (1.5–3 g/day)"
```

### Create Example Data

```bash
python age_clock_calculator.py create-example
```

## Python API

### Calculate PhenoAge

```python
from age_clock_calculator import AgeClockCalculator

calculator = AgeClockCalculator()

# Single subject
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

# Calculate PhenoAge
results = calculator.process_direct_input(biomarker_data)[0]

# Access results
print(f"PhenoAge: {results['phenoage_pheno_age']:.2f} years")
print(f"DNAm Age: {results['phenoage_est_dnam_age']:.2f} years")
print(f"Mortality Score: {results['phenoage_mort_score']:.4f}")
```

### Rank Interventions

```python
# Rank interventions for this individual
rankings = calculator.rank_interventions(biomarker_data)

# Print top 5 interventions
print("\nTop 5 recommended interventions:")
for i, rank in enumerate(rankings[:5]):
    print(f"{i+1}. {rank['intervention']}: reduces biological age by {-rank['delta']:.2f} years")
```

### Simulate Combined Interventions

```python
# Simulate combined effects of multiple interventions
interventions = ["Regular Exercise", "Omega-3 (1.5–3 g/day)", "Berberine (500–1000 mg/day)"]
combined = calculator.simulate_combined_interventions(biomarker_data, interventions)

# Print results
print(f"\nOriginal PhenoAge: {combined['original_pheno_age']:.2f} years")
print(f"New PhenoAge: {combined['new_pheno_age']:.2f} years")
print(f"Improvement: {-combined['delta']:.2f} years")
```

### Process Multiple Subjects

```python
# Multiple subjects
biomarker_data_list = [
    {"albumin": 4.7, "creatinine": 0.8, ...},
    {"albumin": 4.47, "creatinine": 1.17, ...}
]

results_list = calculator.process_direct_input(biomarker_data_list)
for i, result in enumerate(results_list):
    print(f"Subject {i+1} PhenoAge: {result['phenoage_pheno_age']:.2f} years")
```

## Mathematical Details

### PhenoAge Calculation

The PhenoAge calculation follows these steps:

1. **Unit Conversion**:
   - Albumin: g/dL → g/L (multiply by 10)
   - Creatinine: mg/dL → μmol/L (multiply by 88.4)
   - Glucose: mg/dL → mmol/L (multiply by 0.0555)
   - CRP: mg/L → ln(mg/dL) (multiply by 0.1 then take natural log)
   
2. **Apply Weights (from Levine et al. 2018)**:
   - Albumin: -0.0336
   - Creatinine: 0.0095
   - Glucose: 0.1953
   - CRP: 0.0954
   - Lymphocyte: -0.0120
   - MCV: 0.0268
   - RDW: 0.3306
   - Alkaline Phosphatase: 0.0019
   - WBC: 0.0554
   - Chronological Age: 0.0804
   - Intercept: -19.9067

3. **Linear Combination (LinComb)**:
   - Sum of all weighted terms plus intercept
   - LinComb = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ

4. **Mortality Score**:
   ```
   MortScore = 1 - exp(-exp(LinComb) * (exp(g*t) - 1) / g)
   ```
   Where g = 0.0076927 and t = 120 months (10 years)

5. **Calculate PhenoAge**:
   ```
   PhenoAge = 141.50225 + ln(-0.00553 * ln(1 - MortScore)) / 0.090165
   ```

6. **Calculate Estimated DNAm Age**:
   ```
   est_DNAm_Age = PhenoAge / (1 + 1.28047 * exp(0.0344329 * (-182.344 + PhenoAge)))
   ```

7. **Calculate Estimated D MScore**:
   ```
   est_D_MScore = 1 - exp(-0.000520363523 * exp(0.090165 * DNAm_Age))
   ```

### Intervention Ranking System

The intervention ranking system works as follows:

1. For each intervention (25 total):
   - Copy the person's original biomarker values
   - Apply the intervention's specific effects to relevant biomarkers
   - Recalculate PhenoAge with the modified biomarkers
   - Calculate the delta (new PhenoAge - original PhenoAge)

2. Sort interventions by their delta values (ascending)
   - The most negative delta (biggest reduction in PhenoAge) ranks highest

3. Return the ranked list of interventions with their impact

### Combined Intervention Simulation

When simulating multiple interventions together:

1. Start with the original biomarker values
2. Apply each intervention sequentially in the order provided
3. Allow each intervention to further modify biomarkers that have already been changed
4. Calculate the final PhenoAge after all interventions have been applied
5. Return the combined effect and all biomarker changes

Note: The combined effect is not necessarily the sum of individual effects due to:
- Overlapping mechanisms of action
- Diminishing returns when a biomarker approaches optimal levels
- Potential synergistic effects between interventions

## Intervention Details

The calculator includes 25 interventions based on clinical literature. Each intervention has specific effects on different biomarkers:

1. **Regular Exercise**:
   - Reduces CRP (more if elevated)
   - Lowers glucose (5-15 mg/dL)
   - Can reduce WBC if elevated
   - Can increase lymphocyte percentage if low

2. **Weight Loss**:
   - Reduces CRP by 30-40%
   - Lowers glucose by 5-20 mg/dL
   - Can reduce WBC if elevated

3. **Low Allergen / Anti-Inflammatory Diet**:
   - Reduces CRP by 0.2-1.0 mg/L depending on baseline

4. **Curcumin (500-1000 mg/day)**:
   - Reduces CRP significantly (up to 3.7 mg/L if elevated)

5. **Omega-3 (1.5-3 g/day)**:
   - Reduces CRP
   - Can reduce WBC if elevated
   - May increase albumin in inflammatory states
   - Can increase lymphocyte percentage

... and 20 more interventions targeting various biomarkers

## Example Results

Two examples with different biomarker data:

### Example 1: Healthy Biomarkers
```
Baseline PhenoAge: 16.25 years
Estimated DNAm Age: 16.18 years
Mortality Score: 0.0020

Top Interventions:
1. Curcumin (500 mg/day): -0.12 years
2. Omega-3 (1.5–3 g/day): -0.11 years
3. Regular Exercise: -0.09 years
```

### Example 2: Suboptimal Biomarkers
```
Baseline PhenoAge: 51.74 years
Estimated DNAm Age: 51.25 years
Mortality Score: 0.0365

Top Interventions:
1. Weight Loss: -6.35 years
2. Regular Exercise: -5.12 years
3. Curcumin (500 mg/day): -4.78 years
```

## Notes on Large Dataset Processing

When processing large datasets:

1. Ensure your TSV file has these column names (case-sensitive):
   - `albumin`, `creatinine`, `glucose`, `crp`, `lymphocyte`
   - `mcv`, `rdw`, `alkaline_phosphatase`, `wbc`, `chronological_age`

2. If your column names are different, rename them before processing:
   ```python
   import pandas as pd
   df = pd.read_csv("your_dataset.tsv", sep="\t")
   column_mapping = {
       "Age_at_recruitment": "chronological_age",
       "White_blood_cell_count": "wbc",
       # other mappings...
   }
   df_renamed = df.rename(columns=column_mapping)
   df_renamed.to_csv("preprocessed_dataset.tsv", sep="\t", index=False)
   ```

3. For very large files, consider processing in batches or on a machine with ample RAM.

## Requirements

- Python 3.6+
- NumPy
- Pandas
- Math (standard library)

## License

[MIT License](LICENSE)

## Acknowledgments

- PhenoAge calculation based on method by Levine et al. (2018)
- Intervention effects based on systematic review of clinical literature
