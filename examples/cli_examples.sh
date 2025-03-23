#!/bin/bash
# Examples of using the PhenoAge Toolkit CLI

# Create an example TSV file
echo "Creating example TSV file..."
phenoage create-example

# Calculate phenotypic age
echo -e "\n===== CALCULATE PHENOTYPIC AGE ====="
phenoage calculate --albumin 4.2 --creatinine 0.9 --glucose 85 --crp 0.5 \
  --lymphocyte 32 --mcv 88 --rdw 12.9 --alp 62 --wbc 5.2 --age 40

# Calculate percentile
echo -e "\n===== CALCULATE PERCENTILE ====="
phenoage percentile --age 40 --phenoage 35.5

# Rank interventions
echo -e "\n===== RANK INTERVENTIONS ====="
phenoage rank --albumin 4.2 --creatinine 0.9 --glucose 85 --crp 0.5 \
  --lymphocyte 32 --mcv 88 --rdw 12.9 --alp 62 --wbc 5.2 --age 40

# Simulate interventions
echo -e "\n===== SIMULATE INTERVENTIONS ====="
phenoage simulate --albumin 4.2 --creatinine 0.9 --glucose 85 --crp 0.5 \
  --lymphocyte 32 --mcv 88 --rdw 12.9 --alp 62 --wbc 5.2 --age 40 \
  --interventions "Regular Exercise,Omega-3 (1.5–3 g/day)"

# Process TSV file
echo -e "\n===== PROCESS TSV FILE ====="
phenoage process example_biomarkers.tsv --output results.tsv

# Process TSV file with intervention rankings
echo -e "\n===== PROCESS TSV WITH RANKINGS ====="
phenoage process example_biomarkers.tsv --output rankings.tsv --rank

# Process TSV file with interventions
echo -e "\n===== PROCESS TSV WITH INTERVENTIONS ====="
phenoage process example_biomarkers.tsv --output interventions.tsv \
  --apply "Regular Exercise,Omega-3 (1.5–3 g/day)"

# Complete assessment
echo -e "\n===== COMPLETE ASSESSMENT ====="
phenoage assess --albumin 4.2 --creatinine 0.9 --glucose 85 --crp 0.5 \
  --lymphocyte 32 --mcv 88 --rdw 12.9 --alp 62 --wbc 5.2 --age 40

echo -e "\nExamples completed. You can review results in the output files."
