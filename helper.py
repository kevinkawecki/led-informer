# helper.py

import math
import time
import datetime

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

def get_hour():
	hour = time.localtime().tm_hour
	if hour > 12: 
		hour -= 12
	elif hour == 0: 
		hour = 12
	return f"{hour:02d}"

def get_minutes():
	minutes = time.localtime().tm_min
	return f"{minutes:02d}"

def get_month_day_dow():
	today = datetime.date.today()
	month = f"{today.month:02d}"
	month = today.strftime("%b")
	day = f"{today.day:02d}"
	dow = today.strftime("%a")
	return month, day, dow

# find the highest probablility for rain in the next 3 days
#p_max = np.max(hourly_data["precipitation_probability"])
#p_max_index = np.where(hourly_data["precipitation_probability"] == p_max)
#p_time_max = hourly_data["date"][p_max_index]
#print(f"found new max: {p_max_index} : {p_max} at {p_time_max}")