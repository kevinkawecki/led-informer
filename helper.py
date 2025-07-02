# helper.py

import math

def from_minutes(float_minutes):
    """Converts a float representing minutes into minutes and seconds."""
    # Use math.modf() to split the float into its fractional and integer parts.
    # For 2.75, it returns (0.75, 2.0)
    frac_minutes, whole_minutes = math.modf(float_minutes)

    # Convert the integer part to an integer
    whole_minutes = int(whole_minutes)
    
    # Convert the fractional part of minutes to seconds by multiplying by 60
    seconds = int(frac_minutes * 60)
    
    return whole_minutes, seconds