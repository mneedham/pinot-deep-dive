from datetime import datetime
import random
from datetime import timedelta

class Event:
    def __init__(self, id, start:datetime, end:datetime) -> None:
        self.id = id
        self.start = start
        self.end = end        

class EventAttendance:
    def __init__(self, event_id, join:datetime, leave:datetime, join_published:bool=False, leave_published:bool=False) -> None:
        self.event_id = event_id
        self.join = join
        self.leave = leave
        self.join_published = join_published
        self.leave_published = leave_published

    def __str__(self):
        return f"event_id={self.event_id}, join={self.join}, leave={self.leave}"

    @staticmethod   
    def generate(rand_event:Event):
        # event_duration = rand_event.end - rand_event.start
        # join = rand_event.start + timedelta(seconds=random.randint(0, (event_duration - timedelta(seconds=60)).seconds))
        join = rand_event.start + timedelta(seconds=random.randint(0, 10))
        leave = join + timedelta(seconds=random.randint(5, (rand_event.end - join).seconds))

        return EventAttendance(rand_event.id, join, leave)

class Location:
    def __init__(self, ip:str, latLng:str, city:str, region:str) -> None:
        lat, lng = latLng.split(',')
        self.ip = ip
        self.lat=lat
        self.lng=lng
        self.city=city
        self.region=region

class User:
    def __init__(self, id, name, location:Location, next_event:EventAttendance) -> None:
        self.id = id
        self.name = name
        self.location=location
        self.next_event = next_event

    def leave_event(self):
        return {
            "eventTime": datetime.now().isoformat(),
            "eventId": self.next_event.event_id, 
            "userId": self.id, 
            "name": self.name,
            "lat": self.location.lat,
            "lng": self.location.lng,
            "city": self.location.city,
            "region": self.location.region,
            "action": "Leave"
        }

    def join_event(self):
        return  {
            "eventTime": datetime.now().isoformat(),
            "eventId": self.next_event.event_id, 
            "userId": self.id, 
            "name": self.name, 
            "lat": self.location.lat,
            "lng": self.location.lng,
            "city": self.location.city,
            "region": self.location.region,
            "action": "Join"
        }


    def __str__(self):
        return f"id={self.id}, name= {self.name}, next_event={self.next_event}"

