# main.py

import sys
import time
import asyncio

from mta import LTrain
from display import DisplayDriver
from weather import Weather

# globals for when to reach out to servers and get updates
MTA_UPDATE_SEC = 10
ALERT_UPDATE_SEC = 90
WEATHER_UPDATE_SEC = 600 # 10 min  

# init global objects 
display = DisplayDriver()
morganStop = LTrain("L14") # Morgan ave stop id = L14N or L14S
weather = Weather()

# helper functions for piping values into global display obj 
async def updateTrainTimes():
    N_times, S_times = await morganStop.getNextTimes()
    display.setNTimes(N_times)
    display.setSTimes(S_times)

async def updateWeatherInfo():
    cur_temp, daily_info = await weather.getUpdate()
    display.setCurTemp(cur_temp)
    display.setDailyData(daily_info)

async def updateAlerts():
    l_alerts, l_delays = await morganStop.getAlerts()
    # TODO
    # display.setLAlerts(l_alerts)
    # display.setLDelays(l_delays)


async def main(): 

    # run for first time values
    await updateTrainTimes()
    await updateWeatherInfo()
    await updateAlerts()

    try: 
        while True:
            cur_time = time.time()

            if cur_time - morganStop.getLastTime() >= MTA_UPDATE_SEC:
                asyncio.create_task(updateTrainTimes())
                await asyncio.sleep(0)

            if cur_time - weather.getLastTime() >= WEATHER_UPDATE_SEC:
                asyncio.create_task(updateWeatherInfo())
                await asyncio.sleep(0)

            if cur_time - morganStop.getLastAlertTime() >= ALERT_UPDATE_SEC:
                asyncio.create_task(updateAlerts())
                await asyncio.sleep(0)

            # TODO async the display loop, this seems to be hanging worse than
            # the network updates
            # ++ that'll have the bonus of not hanging when running
            # animations!!
            display.loop()

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

