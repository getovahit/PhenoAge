"""
Fix initialization files and test PhenoAge Toolkit
"""
import os
import sys

# Fix __init__.py files
def fix_init_files():
    print("Checking and fixing initialization files...")
    
    # List of directories to check
    dirs = [
        "phenoage_toolkit",
        "phenoage_toolkit/biomarkers",
        "phenoage_toolkit/percentile",
        "phenoage_toolkit/interventions"
    ]
    
    for directory in dirs:
        # Check if _init_.py exists (incorrectly named)
        incorrect_path = os.path.join(directory, "_init_.py")
        correct_path = os.path.join(directory, "__init__.py")
        
        if os.path.exists(incorrect_path):
            print(f"Found incorrectly named {incorrect_path}")
            
            # Read content
            with open(incorrect_path, 'r') as f:
                content = f.read()
            
            # Create correctly named file
            with open(correct_path, 'w') as f:
                f.write(content)
            
            print(f"Created correctly named {correct_path}")
            
            # Optionally rename the old file
            # os.rename(incorrect_path, incorrect_path + ".bak")
            
        elif not os.path.exists(correct_path):
            print(f"Creating empty {correct_path}")
            with open(correct_path, 'w') as f:
                f.write("# Auto-generated __init__.py file")
    
    return True

# Direct import from example_usage.py
def test_toolkit():
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    print("\nTesting direct import from modules...")
    
    try:
        # Try to import API directly as it's shown in example_usage.py
        from phenoage_toolkit.api import PhenoAgeAPI
        
        print("✓ Successfully imported PhenoAgeAPI from api module")
        
        # Initialize API
        api = PhenoAgeAPI()
        
        # Sample biomarker data
        biomarker_data = {
            "albumin": 4.2,              # g/dL
            "creatinine": 0.9,           # mg/dL
            "glucose": 85,               # mg/dL
            "crp": 0.5,                  # mg/L
            "lymphocyte": 32,            # %
            "mcv": 88,                   # fL
            "rdw": 12.9,                 # %
            "alkaline_phosphatase": 62,  # U/L
            "wbc": 5.2,                  # 10^3 cells/µL
            "chronological_age": 40      # years
        }
        
        # Try calculating phenotypic age
        pheno_results = api.calculate_phenoage(biomarker_data)
        
        print("\n===== PHENOAGE CALCULATION RESULTS =====")
        print(f"Chronological Age: {biomarker_data['chronological_age']} years")
        print(f"Phenotypic Age: {pheno_results['pheno_age']:.2f} years")
        
        # Try percentile calculation
        percentile = api.calculate_percentile(
            biomarker_data["chronological_age"], 
            pheno_results["pheno_age"]
        )
        
        print(f"Percentile: {percentile:.2f}")
        
        print("\n✓ Basic functionality test successful!")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        print("\nImport hierarchy check:")
        for module_dir in ["phenoage_toolkit", "phenoage_toolkit/biomarkers", "phenoage_toolkit/percentile", "phenoage_toolkit/interventions"]:
            if os.path.exists(os.path.join(module_dir, "__init__.py")):
                print(f"  ✓ {module_dir}/__init__.py exists")
            else:
                print(f"  ✗ {module_dir}/__init__.py missing")
        return False

if __name__ == "__main__":
    # Fix initialization files
    if fix_init_files():
        # Test the toolkit
        test_toolkit()