# test.py 

import sys
import asyncio

from mta import LTrain
from helper import from_minutes, get_hour, get_minutes, get_month_day_dow
from weather import Weather

UPDATE_SEC = 10

# Morgan ave stop id = L14N or L14S
morganStop = LTrain("L14")

#l_alerts, l_delays = morganStop.getAlerts()
#print(l_alerts)
#print(l_delays)

async def main(): 
	#N_times, S_times = morganStop.getNextTimes()
	l_alerts, l_delays = await morganStop.getAlerts()

if __name__ == "__main__":
    asyncio.run(main())

sys.exit(0)

if len(N_times) > 0:
	min, sec = from_minutes(N_times[0])
	print(f"Next Man: {min}:{sec}")
else: 
	print("N L down")

if len(S_times) > 0:
	min, sec = from_minutes(S_times[0])
	print(f"Next Can: {min}:{sec}")
else: 
	print("S L down")

print(f"{get_hour()}:{get_minutes()}")

month, day, dow = get_month_day_dow()
print(f"{month}/{day} {dow}")

weather = Weather()

