# main.py

import time
import math

from mta import LTrain
from helper import from_minutes
from display import DisplayDriver

UPDATE_SEC = 10

# Morgan ave stop id = L14N or L14S
morganStop = LTrain("L14")

display = DisplayDriver()

N_times, S_times = morganStop.getNextTimes()
display.setNTimes(N_times)
display.setSTimes(S_times)

count = 0

try: 
    while True:
        if count > UPDATE_SEC:
            count = 0
            N_times, S_times = morganStop.getNextTimes()
            display.setNTimes(N_times)
            display.setSTimes(S_times)

        display.loop()

        time.sleep(1)
        count += 1

except KeyboardInterrupt:
    sys.exit(0)
