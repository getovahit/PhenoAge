"""
Unit tests for the CLI module.

Note: These tests patch sys.argv and capture stdout to test CLI functionality
without actually running the CLI as a subprocess.
"""

import unittest
import io
import sys
import os
import tempfile
import json
from unittest.mock import patch
from contextlib import redirect_stdout
import pandas as pd
from phenoage_toolkit import cli


class TestCLI(unittest.TestCase):
    """Test the CLI module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample CLI arguments
        self.sample_biomarker_args = [
            "--albumin", "4.2",
            "--creatinine", "0.9",
            "--glucose", "90",
            "--crp", "0.5",
            "--lymphocyte", "35",
            "--mcv", "90",
            "--rdw", "13.0",
            "--alp", "70",
            "--wbc", "5.5",
            "--age", "45"
        ]
        
        # Create a temporary directory for output files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        self.temp_dir.cleanup()
        
    def capture_output(self, argv):
        """Capture stdout output from CLI function."""
        buffer = io.StringIO()
        with patch.object(sys, 'argv', argv):
            with redirect_stdout(buffer):
                try:
                    cli.main()
                except SystemExit:
                    pass  # Ignore system exit
        return buffer.getvalue()

    def test_help_text(self):
        """Test that help text is shown."""
        # Capture help output
        output = self.capture_output(['phenoage', '--help'])
        
        # Should contain key help text
        self.assertIn("PhenoAge Toolkit", output)
        self.assertIn("Command to execute", output)
        
    def test_calculate_command(self):
        """Test the calculate command."""
        # Capture calculate output
        output = self.capture_output(['phenoage', 'calculate'] + self.sample_biomarker_args)
        
        # Should contain calculation results
        self.assertIn("PhenoAge Calculation Results", output)
        self.assertIn("PhenoAge:", output)
        self.assertIn("Mortality Score:", output)
        
    def test_percentile_command(self):
        """Test the percentile command."""
        # Capture percentile output
        output = self.capture_output(['phenoage', 'percentile', '--age', '45', '--phenoage', '40'])
        
        # Should contain percentile assessment
        self.assertIn("PHENOTYPIC AGE ASSESSMENT", output)
        self.assertIn("percentile", output.lower())
        self.assertIn("Reference Values", output)
        
    def test_rank_command(self):
        """Test the rank command."""
        # Capture rank output
        output = self.capture_output(['phenoage', 'rank'] + self.sample_biomarker_args)
        
        # Should contain intervention rankings
        self.assertIn("Baseline PhenoAge:", output)
        self.assertIn("Interventions ranked by improvement", output)
        self.assertIn("years", output)
        
    def test_simulate_command(self):
        """Test the simulate command."""
        # Capture simulate output
        output = self.capture_output([
            'phenoage', 'simulate'] + self.sample_biomarker_args + [
            '--interventions', 'Regular Exercise,Omega-3 (1.5–3 g/day)'
        ])
        
        # Should contain simulation results
        self.assertIn("Combined Intervention Simulation", output)
        self.assertIn("Original PhenoAge:", output)
        self.assertIn("New PhenoAge:", output)
        self.assertIn("Improvement:", output)
        self.assertIn("Percentile Improvement:", output)
        self.assertIn("Biomarker Changes:", output)
        
    def test_assess_command(self):
        """Test the assess command."""
        # Capture assess output
        output = self.capture_output(['phenoage', 'assess'] + self.sample_biomarker_args)
        
        # Should contain complete assessment
        self.assertIn("PHENOTYPIC AGE ASSESSMENT", output)
        self.assertIn("INTERVENTION RECOMMENDATIONS", output)
        self.assertIn("Chronological Age:", output)
        self.assertIn("Phenotypic Age:", output)
        self.assertIn("Percentile:", output)
        
    def test_assess_with_output_file(self):
        """Test the assess command with output to file."""
        # Create output file path
        output_file = os.path.join(self.temp_dir.name, "assessment.json")
        
        # Run CLI command
        output = self.capture_output([
            'phenoage', 'assess'] + self.sample_biomarker_args + [
            '--output', output_file
        ])
        
        # File should exist
        self.assertTrue(os.path.exists(output_file))
        
        # File should contain valid JSON
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        # JSON should have expected keys
        self.assertIn("chronological_age", data)
        self.assertIn("phenotypic_age", data)
        self.assertIn("percentile", data)
        self.assertIn("intervention_rankings", data)
        
    def test_create_example_command(self):
        """Test the create-example command."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(self.temp_dir.name)
        
        try:
            # Capture create-example output
            output = self.capture_output(['phenoage', 'create-example'])
            
            # File should exist
            self.assertTrue(os.path.exists("example_biomarkers.tsv"))
            
            # Output should mention the file
            self.assertIn("Created example_biomarkers.tsv", output)
            
            # File should be valid TSV
            df = pd.read_csv("example_biomarkers.tsv", sep='\t')
            self.assertGreater(len(df), 0)
            
            # Should have required columns
            required_columns = [
                "albumin", "creatinine", "glucose", "crp", "lymphocyte",
                "mcv", "rdw", "alkaline_phosphatase", "wbc", "chronological_age"
            ]
            for column in required_columns:
                self.assertIn(column, df.columns)
        finally:
            # Change back to original directory
            os.chdir(original_dir)


if __name__ == "__main__":
    unittest.main()
