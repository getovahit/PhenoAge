import sys
import os

# Add the current directory to Python path
current_dir = os.getcwd()
sys.path.append(current_dir)

# Try to locate the main package files
print(f"Looking for PhenoAge modules in: {current_dir}")
print("Python modules found:")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            print(os.path.join(root, file))

# Let's try to directly import the modules based on the repository structure
try:
    # Attempt direct import from the modules
    # Assuming structure based on documentation
    sys.path.insert(0, os.path.join(current_dir, 'phenoage_toolkit'))
    
    # Import core functionality (modify paths based on actual structure)
    from phenoage_toolkit.biomarkers.calculator import AgeClockCalculator
    
    print("\nSuccessfully imported AgeClockCalculator!")
    
    # Test with sample data
    calculator = AgeClockCalculator()
    
    # Sample biomarker data
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
    pheno_results = calculator.calculate_phenoage(biomarker_data)
    print("\nPhenoAge Calculation Results:")
    print(f"Phenotypic Age: {pheno_results['phenotypic_age']:.2f} years")
    
    # Try to import percentile calculator
    from phenoage_toolkit.percentile.calculator import calculate_percentile
    
    percentile = calculate_percentile(30, pheno_results['phenotypic_age'])
    print(f"Percentile Rank: {percentile:.2f}")
    
except ImportError as e:
    print(f"\nImport Error: {e}")
    print("\nTrying alternative approach...")
    
    # If the import fails, let's try to find the right structure
    module_paths = []
    for root, dirs, files in os.walk('.'):
        if "__init__.py" in files:
            module_paths.append(root)
    
    print("\nPotential module paths found:")
    for path in module_paths:
        print(path)
        
    print("\nPlease check the actual structure and modify imports accordingly")