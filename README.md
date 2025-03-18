# Age Clock Calculator

A Python toolkit for calculating biological age clocks based on biomarker data. Currently supports PhenoAge calculation, with extensibility for additional age clocks.

## Overview

The Age Clock Calculator provides a simple and flexible way to estimate biological age based on standard clinical biomarkers. It can be used:

1. As a standalone command-line tool
2. As a Python library in data analysis workflows
3. Integrated into production pipelines

The calculator converts biomarker units, applies scientifically validated weights, and computes age-related metrics using established algorithmic formulas.

## Features

- **PhenoAge Calculation**: Implements the Levine et al. method for phenotypic age estimation
- **Flexible Input**: Accepts biomarker data from either TSV files or direct Python dictionaries
- **Multiple Output Formats**: Results available as TSV, CSV, Excel, JSON, or Python objects
- **Biomarker Name Aliases**: Recognizes different naming conventions for the same biomarker
- **Error Handling**: Provides informative errors about missing or invalid biomarkers
- **Well-Documented API**: Clear documentation for all methods and parameters

## Installation

```bash
# Clone the repository
git clone https://github.com/getovahit/PhenoAge.git
cd age-clock-calculator

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
| WBC                   | 10^3 cells/mL     | White blood cell count         |
| Chronological Age     | years             | Patient's chronological age    |

## Usage

### Command Line Interface

#### Create Example Data

```bash
python age_clock_calculator.py create-example
```

This creates a file `example_biomarkers.tsv` with sample data in the correct format.

#### Process a TSV File

```bash
python age_clock_calculator.py process example_biomarkers.tsv --output results.tsv
```

Processes all rows in the TSV file and outputs results to the specified file.

#### Calculate for a Single Set of Biomarkers

```bash
python age_clock_calculator.py calculate --albumin 4.7 --creatinine 0.8 --glucose 75.9 --crp 0.1 --lymphocyte 57.5 --mcv 92.9 --rdw 13.3 --alp 15 --wbc 4.1 --age 30
```

Calculates age clock values for a single set of biomarkers provided directly.

### Python API

#### Process TSV File

```python
from age_clock_calculator import AgeClockCalculator

calculator = AgeClockCalculator()
results_df = calculator.process_tsv_file('example_biomarkers.tsv')

# Access results
for index, row in results_df.iterrows():
    print(f"Subject {row.get('ID', index)}:")
    print(f"  PhenoAge: {row['phenoage_pheno_age']:.2f} years")
    print(f"  DNAm Age: {row['phenoage_est_dnam_age']:.2f} years")
```

#### Direct Integration (Recommended for Production)

```python
from age_clock_calculator import AgeClockCalculator

# Initialize the calculator
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
    "wbc": 4.1,                     # 10^3 cells/mL
    "chronological_age": 30         # years
}

# Process the data
results = calculator.process_direct_input(biomarker_data)[0]

# Access results
pheno_age = results['phenoage_pheno_age']
dnam_age = results['phenoage_est_dnam_age']
mort_score = results['phenoage_mort_score']

print(f"PhenoAge: {pheno_age:.2f} years")
print(f"DNAm Age: {dnam_age:.2f} years")
print(f"Mortality Score: {mort_score:.4f}")

# Multiple subjects
biomarker_data_list = [
    {"albumin": 4.7, "creatinine": 0.8, ...},
    {"albumin": 4.47, "creatinine": 1.17, ...}
]

results_list = calculator.process_direct_input(biomarker_data_list)
for i, result in enumerate(results_list):
    print(f"Subject {i+1} PhenoAge: {result['phenoage_pheno_age']:.2f} years")
```

## Example Results

Two examples with different biomarker data:

### Example 1
```
Biomarker Data:
- Albumin: 4.7 g/dL
- Creatinine: 0.8 mg/dL
- Glucose: 75.9 mg/dL
- CRP: 0.1 mg/L
- Lymphocyte: 57.5 %
- MCV: 92.9 fL
- RDW: 13.3 %
- Alkaline Phosphatase: 15 U/L
- WBC: 4.1 10^3 cells/mL
- Chronological Age: 30 years

Results:
- Linear Combination: -11.5664
- Mortality Score: 0.0020
- PhenoAge: 16.25 years
- Estimated DNAm Age: 16.18 years
- Estimated D MScore: 0.0020
```

### Example 2
```
Biomarker Data:
- Albumin: 4.47 g/dL
- Creatinine: 1.17 mg/dL
- Glucose: 77 mg/dL
- CRP: 0.07 mg/L
- Lymphocyte: 36 %
- MCV: 90 fL
- RDW: 13.7 %
- Alkaline Phosphatase: 54 U/L
- WBC: 4.5 10^3 cells/mL
- Chronological Age: 46 years

Results:
- Linear Combination: -9.5053
- Mortality Score: 0.0153
- PhenoAge: 38.74 years
- Estimated DNAm Age: 38.39 years
- Estimated D MScore: 0.0160
```

## Calculation Details

The PhenoAge calculation follows these steps:

1. **Unit Conversion**: Convert biomarkers to required units
   - Albumin: g/dL → g/L (multiply by 10)
   - Creatinine: mg/dL → μmol/L (multiply by 88.4)
   - Glucose: mg/dL → mmol/L (multiply by 0.0555)
   - CRP: mg/L → ln(mg/dL) (multiply by 0.1 then take natural log)
   
2. **Apply Weights**: Multiply each converted biomarker by its weight
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

3. **Calculate Linear Combination**: Sum of all weighted terms plus intercept

4. **Calculate Mortality Score**:
   ```
   MortScore = 1 - EXP(-EXP(LinComb) * (EXP(g*t) - 1) / g)
   ```
   Where g = 0.0076927 and t = 10 years

5. **Calculate PhenoAge**:
   ```
   PhenoAge = 141.50225 + LN(-0.00553 * LN(1 - MortScore)) / 0.09165
   ```

6. **Calculate Estimated DNAm Age**:
   ```
   estDNAm Age = PhenoAge / (1 + 1.28047 * EXP(0.0344329 * (-182.344 + PhenoAge)))
   ```

7. **Calculate Estimated D MScore**:
   ```
   est D MScore = 1 - EXP(-0.000520363523 * EXP(0.090165 * DNAm Age))
   ```

## Adding New Age Clocks

The calculator is designed to be easily extended with additional age clocks:

1. Add a new calculation method in the `AgeClockCalculator` class
2. Update the `available_clocks` list in the `__init__` method
3. Add any necessary constants or weights

Example for implementing a new age clock:

```python
def calculate_new_clock(self, biomarker_data):
    # Your implementation here
    return {
        "metric1": value1,
        "metric2": value2,
        # More metrics...
    }
```

## Notes on Production Integration

For production environments, we recommend:

1. Using the `process_direct_input()` method which accepts dictionaries directly
2. Adding appropriate error handling around the calculator
3. Validating biomarker data before passing to the calculator
4. Considering caching results for repeated calculations

Example integration with error handling:

```python
try:
    results = calculator.process_direct_input(biomarker_data)
    
    # Check for errors in results
    for result in results:
        if 'error' in result:
            log_error(f"Calculation error: {result['error']}")
            # Handle error accordingly
        
except Exception as e:
    log_error(f"Calculator exception: {str(e)}")
    # Handle exception accordingly
```

## Requirements

- Python 3.6+
- NumPy
- Pandas
- Math (standard library)

## License

[MIT License](LICENSE)

## Acknowledgments

- Based on the PhenoAge calculation method by Levine et al.

