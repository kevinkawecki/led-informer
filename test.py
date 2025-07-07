# test.py 

from mta import LTrain
from helper import from_minutes, get_hour, get_minutes, get_month_day_dow
from weather import Weather

UPDATE_SEC = 10

# Morgan ave stop id = L14N or L14S
morganStop = LTrain("L14")

N_times, S_times = morganStop.getNextTimes()

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

