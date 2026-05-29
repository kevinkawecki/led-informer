# mta.py

import datetime
import time
import requests
import asyncio
from google.transit import gtfs_realtime_pb2

LTRAIN_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l"
#STOP_ID = "L14"
ALERTS_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
#"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"

class LTrain:
    def __init__(self, stop_id):
        self.STOP_ID = stop_id
        self.findStopN = f"{stop_id}N"
        self.findStopS = f"{stop_id}S"
        self.lastTime = time.time()
        self.lastAlertTime = time.time()

    def getLastTime(self):
        return self.lastTime
    
    def getLastAlertTime(self):
        return self.lastAlertTime
    
    async def getNextTimes(self):
        try: 
            feed = gtfs_realtime_pb2.FeedMessage()
            response = requests.get(LTRAIN_URL)
            if response.status_code != 200:
                _LOGGER.error("updating route status got {}:{}".format(response.status_code,response.content))
            feed.ParseFromString(response.content)
            departure_times = {}

            N_times = []
            S_times = []
            
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    for stop in entity.trip_update.stop_time_update:
                        stop_id = stop.stop_id
                        if stop_id in self.findStopN or stop_id in self.findStopS: 
                            # Keep only future arrival.time (gtfs data can give past arrival.time, which is useless and show negative time as result)
                            now = time.time()
                            if int(stop.arrival.time) > int(now):
                                #print(f"Upcoming arrival time: {stop.arrival.time}")
                                time_difference = stop.arrival.time - now
                                #print(f"time_difference: {time_difference}")
                                minutes_from_now = time_difference / 60
                                #print(f"Minutes from now: {minutes_from_now}")
                                if stop_id in self.findStopN:
                                    N_times.append(minutes_from_now)
                                elif stop_id in self.findStopS: 
                                    S_times.append(minutes_from_now)

            N_times_next_3 = N_times[:3]
            S_times_next_3 = S_times[:3]
            self.lastTime = time.time()
            return N_times_next_3, S_times_next_3

        except Exception as e:
            print(e)
            print("getNextTimes Failed!")
            return [], [] 


    async def getAlerts(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        response = requests.get(ALERTS_URL)
        if response.status_code != 200:
            _LOGGER.error("updating alert status got {}:{}".format(response.status_code,response.content))
        feed.ParseFromString(response.content)

        l_alerts = []
        l_delays = []

        for entity in feed.entity: 
            if entity.HasField('alert'):
                for informed in entity.alert.informed_entity:
                    if informed.route_id == "L":
                        # set vars if they exist in the object 
                        try: 
                            header_text = entity.alert.header_text.translation[0].text
                        except: 
                            header_text = ""

                        try:
                            description_text = entity.alert.description_text.translation[0].text
                        except: 
                            description_text = ""

                        if "no [L]" in header_text or "shuttle bus" in description_text.lower() \
                                or "delays" in header_text.lower(): #or "track maintenance" in description_text.lower():
                            active_periods = []
                            for period in entity.alert.active_period:
                                start_date = datetime.datetime.fromtimestamp(period.start).strftime('%m/%d') if period.start else "N/A"
                                start_time = datetime.datetime.fromtimestamp(period.start).strftime('%H:%M') if period.start else "N/A"
                                end_date = datetime.datetime.fromtimestamp(period.end).strftime('%m/%d') if period.end else "Ongoing"
                                end_time = datetime.datetime.fromtimestamp(period.end).strftime('%H:%M') if period.end else "Ongoing"
                                active_periods.append({ 
                                    "start_date": start_date, 
                                    "start_time": start_time, 
                                    "end_date": end_date, 
                                    "end_time": end_time, 
                                    "start_full": period.start,
                                    "end_full": period.end,
                                })

                            # consolidate active_periods to get only the first and last planned days
                            if len(active_periods) > 2:
                                first_in_streak = active_periods[0]
                                last_in_streak = active_periods[0]
                                result = []
                                for i in range(1, len(active_periods)):
                                    curr = active_periods[i]
                                    prev = active_periods[i-1]

                                    curr_date =  datetime.datetime.strptime(curr["start_date"], "%m/%d")
                                    prev_date =  datetime.datetime.strptime(prev["start_date"], "%m/%d")

                                    times_match =  (curr["start_time"] == prev["start_time"] and curr["end_time"] == prev["end_time"])

                                    is_one_day_later = (curr_date - prev_date).days == 1

                                    is_consecutive = times_match and is_one_day_later

                                    if is_consecutive:
                                        last_in_streak = curr
                                    else:
                                        # New Streak! Capture it..
                                        result.append(first_in_streak)
                                        if last_in_streak != first_in_streak:
                                            result.append(last_in_streak)

                                        # Setup for the next streak 
                                        first_in_streak = curr
                                        last_in_streak = curr

                                # Catch the last streak
                                result.append(first_in_streak)
                                if last_in_streak != first_in_streak:
                                    result.append(last_in_streak)

                                # DEBUG 
                                if False:
                                    print(" ")
                                    print("Current list: ")
                                    for period in result:
                                        print(period)
                                    print(" ")

                                if len(result) > 0:
                                    active_periods = result


                            if "delays" in header_text.lower():
                                l_delays.append({
                                    "header": header_text,
                                    #"description": description_text,
                                    "periods": active_periods
                                })
                            else:
                                l_alerts.append({
                                    "header": header_text,
                                    #"description": description_text,
                                    "periods": active_periods
                                })
                        break

        # DEBUG
        if False:
            print(" ")
            print("-----------------------------------")
            print(l_alerts)
            print(l_delays)

        self.lastAlertTime = time.time()
        return l_alerts, l_delays
