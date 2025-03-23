import numpy as np
from scipy.stats import norm

# Standard deviation of phenotypic age based on the observed data spread
STD_DEV = 5.5  # years


def calculate_percentile(chronological_age, phenotypic_age):
    """
    Calculate the percentile for a given phenotypic age compared to chronological age peers.
    Uses a simple normal distribution approximation.
    
    Higher percentile = biologically younger than peers (better outcome).
    
    Parameters:
    -----------
    chronological_age : float
        The person's chronological age in years
    phenotypic_age : float
        The person's phenotypic (biological) age in years
        
    Returns:
    --------
    float
        The percentile value (0-100)
    """
    # Calculate z-score (negative z = younger biological age = better)
    z_score = (phenotypic_age - chronological_age) / STD_DEV
    
    # Convert to percentile (inverted because lower phenotypic age is better)
    percentile = (1 - norm.cdf(z_score)) * 100
    
    return percentile


def get_reference_values(chronological_age):
    """
    Get reference phenotypic age values for different percentiles at a given chronological age.
    
    Parameters:
    -----------
    chronological_age : float
        Chronological age in years
        
    Returns:
    --------
    dict
        Dictionary with reference values for different percentiles
    """
    # Calculate phenotypic age for different percentiles
    # For percentile p, we need the (1-p)th quantile because lower is better
    references = {
        '10th': chronological_age + STD_DEV * norm.ppf(0.9),  # Worse than 90% (older biological age)
        '25th': chronological_age + STD_DEV * norm.ppf(0.75), # Worse than 75% (older biological age)
        '50th': chronological_age,                            # Median
        '75th': chronological_age + STD_DEV * norm.ppf(0.25), # Better than 75% (younger biological age)
        '90th': chronological_age + STD_DEV * norm.ppf(0.1)   # Better than 90% (younger biological age)
    }
    
    return references


def interpret_percentile(percentile):
    """
    Provide a human-readable interpretation of the percentile.
    
    Parameters:
    -----------
    percentile : float
        Percentile score (0-100)
        
    Returns:
    --------
    str
        Human-readable interpretation of the percentile
    """
    if percentile >= 90:
        return "Excellent - younger biological age than 90% of people your age"
    elif percentile >= 75:
        return "Very good - younger biological age than 75% of people your age"
    elif percentile >= 50:
        return "Good - younger biological age than average"
    elif percentile >= 25:
        return "Below average - older biological age than average"
    elif percentile >= 10:
        return "Poor - older biological age than 75% of people your age"
    else:
        return "Concerning - older biological age than 90% of people your age"
