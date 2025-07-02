# test.py 

import time
import math

from mta import LTrain
from helper import from_minutes
from display import DisplayDriver

UPDATE_SEC = 10

# Morgan ave stop id = L14N or L14S
morganStop = LTrain("L14")

N_times, S_times = morganStop.getNextTimes()
display.setNTimes(N_times)
display.setSTimes(S_times)

print(N_times)
print(S_times)

