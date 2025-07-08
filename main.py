# main.py

import sys
import time

from mta import LTrain
from display import DisplayDriver
from weather import Weather

# globals for when to reach out to servers and get updates
MTA_UPDATE_SEC = 10
WEATHER_UPDATE_SEC = 1800 # 30 min  
mta_count = 0
weather_count = 0

display = DisplayDriver()

# Init objects and get first values
# Morgan ave stop id = L14N or L14S
morganStop = LTrain("L14")
N_times, S_times = morganStop.getNextTimes()
display.setNTimes(N_times)
display.setSTimes(S_times)

weather = Weather()
cur_temp, daily_info = weather.getUpdate()
display.setCurTemp(cur_temp)
display.setDailyData(daily_info)

try: 
	while True:
		if mta_count >= MTA_UPDATE_SEC:
			N_times, S_times = morganStop.getNextTimes()
			display.setNTimes(N_times)
			display.setSTimes(S_times)
			mta_count = 0

		if weather_count >= WEATHER_UPDATE_SEC:
			cur_temp, daily_info = weather.getUpdate()
			display.setCurTemp(cur_temp)
			display.setDailyData(daily_info)
			weather_count = 0

		display.loop()

		time.sleep(1)
		mta_count += 1
		weather_count += 1

except KeyboardInterrupt:
	sys.exit(0)
