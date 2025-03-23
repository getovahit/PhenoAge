"""
PhenoAge Toolkit - A modular toolkit for biological age calculations and interventions.

This package provides tools for:
1. Calculating phenotypic age from biomarkers
2. Determining percentile ranks compared to age peers
3. Ranking interventions by their potential to reduce biological age
4. Simulating the effects of lifestyle and supplementation interventions

Main components:
- API: Unified interface for all functionality
- Biomarkers: PhenoAge calculations
- Percentile: Statistical positioning within age peers
- Interventions: Models for biomarker improvements
"""

from .api import PhenoAgeAPI

__version__ = "1.0.0"
