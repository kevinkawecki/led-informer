import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import numpy as np

class Weather: 
	def __init__(self):
		# Setup the Open-Meteo API client with cache and retry on error
		self.cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
		self.retry_session = retry(self.cache_session, retries = 5, backoff_factor = 0.2)
		self.openmeteo = openmeteo_requests.Client(session = self.retry_session)

		# Make sure all required weather variables are listed here
		# The order of variables in hourly or daily is important to assign them correctly below
		self.url = "https://api.open-meteo.com/v1/forecast"
		self.params = {
			"latitude": 40.705834,
			"longitude": -73.930478,
			"daily": ["weather_code", "precipitation_probability_max", "apparent_temperature_max", "apparent_temperature_min", "precipitation_hours"],
			"hourly": ["precipitation_probability", "apparent_temperature"],
			"current": ["apparent_temperature", "weather_code"],
			"timezone": "America/New_York",
			"forecast_days": 3,
			"wind_speed_unit": "mph",
			"temperature_unit": "fahrenheit",
			"precipitation_unit": "inch"
		}

		self.cur_temp = 0
		self.daily_info = []

		self.getNextWeather()

	def getNextWeather(self):
		responses = self.openmeteo.weather_api(self.url, params=self.params)

		# Process first location. Add a for-loop for multiple locations or weather models
		response = responses[0]
		#print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
		#print(f"Elevation {response.Elevation()} m asl")
		#print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
		#print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

		# Current values. The order of variables needs to be the same as requested.
		current = response.Current()
		current_apparent_temperature = current.Variables(0).Value()
		#current_weather_code = current.Variables(1).Value()
		self.cur_temp = current_apparent_temperature

		#print(f"Current time {current.Time()}")
		#print(f"Current apparent_temperature {current_apparent_temperature}")
		#print(f"Current weather_code {current_weather_code}")

		# Process hourly data. The order of variables needs to be the same as requested.
		hourly = response.Hourly()
		hourly_precipitation_probability = hourly.Variables(0).ValuesAsNumpy()
		hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()

		hourly_data = {"date": pd.date_range(
			start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
			end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = hourly.Interval()),
			inclusive = "left"
		)}

		hourly_data["precipitation_probability"] = hourly_precipitation_probability
		hourly_data["apparent_temperature"] = hourly_apparent_temperature

		hourly_dataframe = pd.DataFrame(data = hourly_data)
		print(hourly_dataframe)

		# Process daily data. The order of variables needs to be the same as requested.
		daily = response.Daily()
		daily_weather_code = daily.Variables(0).ValuesAsNumpy()
		daily_precipitation_probability_max = daily.Variables(1).ValuesAsNumpy()
		daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
		daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
		daily_precipitation_hours = daily.Variables(4).ValuesAsNumpy()

		daily_data = {"date": pd.date_range(
			start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
			end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = daily.Interval()),
			inclusive = "left"
		)}

		daily_data["weather_code"] = daily_weather_code
		daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
		daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
		daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
		daily_data["precipitation_hours"] = daily_precipitation_hours

		daily_dataframe = pd.DataFrame(data = daily_data)
		print(daily_dataframe)