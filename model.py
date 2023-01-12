from datetime import datetime
import random
from datetime import timedelta
from faker import Faker


fake = Faker()

class Event:
    def __init__(self, id:str, start:datetime, end:datetime) -> None:
        self.id = id
        self.start = start
        self.end = end

    @staticmethod
    def generate(start_time:datetime, min_event_length:int, max_event_length:int):

        return Event(
            id=fake.uuid4(),
            start=start_time,
            end=start_time + timedelta(seconds=random.uniform(min_event_length, max_event_length))
        )

    def __str__(self):
        return f"Event(id={self.id}, start={self.start}, end={self.end})"

    def __repr__(self):
        return self.__str__()

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
    def generate(event:Event):
        earliest_join = max(event.start, datetime.now())
        time_left = event.end - earliest_join

        join = min(earliest_join + timedelta(seconds=random.uniform(0, min(time_left.seconds, 5))), event.end)
        leave = min(join + timedelta(seconds=random.uniform(5, ((event.end-join) - timedelta(seconds=1)).seconds)), event.end)

        return EventAttendance(event.id, join, leave)

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
            "eventTime": self.next_event.leave.isoformat(),
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
            "eventTime": self.next_event.join.isoformat(),
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
        return f"User(id={self.id}, name= {self.name}, next_event={self.next_event})"

    def __repr__(self):
        return self.__str__()