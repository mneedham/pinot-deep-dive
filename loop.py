import click
import datetime
import json

from twisted.internet import task, reactor
from faker import Faker
from datetime import datetime, timedelta
from model import *

fake = Faker()
all_events:dict[str, Event] = {}
all_users:dict[str, User] = {}

with open('data/ips.json', 'r') as ips_file:
    ips = [json.loads(line) for line in ips_file.readlines()]
    ips = [ip for ip in ips if "region" in ip]

with open('data/event_names.json', 'r') as event_names_file:
    event_names = [json.loads(line) for line in event_names_file.readlines()]

def emitJoins():
    joins = [user 
        for _, user in all_users.items()
        if user.next_event.join < datetime.now() and (not user.next_event.join_published)
    ]
    for user in joins:
        user.next_event.join_published = True
        print(json.dumps(user.join_event()))


def emitLeaves():
    leaves = [user
        for _, user in all_users.items() 
        if user.next_event.leave  < datetime.now() and (not user.next_event.leave_published)
    ]
    for user in leaves:
        user.next_event.leave_published = True
        print(json.dumps(user.leave_event()))
        user.next_event = EventAttendance.generate(get_random_event())

def refreshEvents(min_event_length, max_event_length):
    finished_events = [event for _, event in all_events.items() if event.end > datetime.now()]
    for k in finished_events:
        all_events.pop(k, None)
        start = datetime.now()
        event = Event.generate(start, min_event_length, max_event_length)
        all_events[event.id] = event
    

def get_random_event():
    event_ids = [event_id for event_id,event in all_events.items() if event.end > (datetime.now() + timedelta(seconds=5))]
    random_event_id = event_ids[random.randint(0, len(event_ids)-1)]
    return all_events[random_event_id]

@click.command()
@click.option('--timeout', default=1, help='Run loop every <n> seconds')
@click.option('--users', default=10, help='Number of users')
@click.option('--events', default=10, help='Number of events')
@click.option('--max-start-delay', default=60, help='The maximum delay of the start time of events (in seconds)')
@click.option('--min-event-length', default=300, help='The minimum length of an event (in seconds)')
@click.option('--max-event-length', default=600, help='The maximum length of an event (in seconds)')
def run_loop(timeout, users, events, max_start_delay, min_event_length, max_event_length):
    """Generates an event stream for an online livestream"""
    for idx in range(0, events):
        start = datetime.now() + timedelta(seconds=random.uniform(0, max_start_delay))
        event = Event.generate(start, min_event_length, max_event_length)
        all_events[event.id] = event

    for i in range(0, users):
        name = fake.name()
        uuid = fake.uuid4()
        ip = ips[random.randint(0, len(ips)-1)]

        all_users[uuid] = User(
            id=uuid,
            name=name,
            location = Location(ip = ip["ip"], latLng=ip["loc"], city=ip["city"], region=ip["region"]),
            next_event = EventAttendance.generate(get_random_event())
        )

    l = task.LoopingCall(emitJoins)
    l.start(timeout)

    l = task.LoopingCall(emitLeaves)
    l.start(timeout)

    l = task.LoopingCall(refreshEvents, min_event_length, max_event_length)
    l.start(timeout)

    reactor.run()

if __name__ == '__main__':
    run_loop()