# main.py

import sys
import time
import asyncio

from mta import LTrain
from display import DisplayDriver
from weather import Weather

# globals for when to reach out to servers and get updates
MTA_UPDATE_SEC = 10
ALERT_UPDATE_SEC = 600
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
    display.setAlerts(l_alerts)
    display.setDelays(l_delays)

from curtsies import Input

async def handle_input(x_offset, y_offset):
    """Asynchronously processes keyboard input."""
    # Input(keynames='curtsies') makes arrow keys return '<UP>', '<DOWN>', etc.
    with Input(keynames='curtsies') as input_generator:
        for key in input_generator:
            if key == '<UP>':
                y_offset -= 1
                return x_offset, y_offset
            elif key == '<DOWN>':
                y_offset += 1
                return x_offset, y_offset
            elif key == '<RIGHT>':
                x_offset += 1
                return x_offset, y_offset
            elif key == '<LEFT>':
                x_offset -= 1
                return x_offset, y_offset

            # Yield control back to the event loop
            await asyncio.sleep(0)

async def main(): 

    # run for first time values
    await updateTrainTimes()
    await updateWeatherInfo()
    await updateAlerts()

    x_offset = 0
    y_offset = 0

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
            asyncio.create_task(display.loop(x_offset, y_offset))
            #output = await asyncio.gather(display.loop(x_offset, y_offset), handle_input(x_offset, y_offset))
            #x_offset, y_offset = output[1]
            #print(f"{x_offset}, {y_offset}")

            await asyncio.sleep(.08)

    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

