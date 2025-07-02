# mta.py

import datetime
import time
import requests
from google.transit import gtfs_realtime_pb2

LTRAIN_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l"
#STOP_ID = "L14"

class LTrain:
    def __init__(self, stop_id):
        self.STOP_ID = stop_id
        self.findStopN = f"{stop_id}N"
        self.findStopS = f"{stop_id}S"
    
    def getNextTimes(self):
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

        N_times_next_3 = N_times[:5]
        S_times_next_3 = S_times[:5]
        return N_times_next_3, S_times_next_3
