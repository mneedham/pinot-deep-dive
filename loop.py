import click
from twisted.internet import task, reactor
import datetime
from faker import Faker
import json
import random

from datetime import datetime, timedelta

from model import *

fake = Faker()
all_events = {}
all_users = {}

with open('data/ips.json', 'r') as ips_file:
    ips = [json.loads(line) for line in ips_file.readlines()]
    ips = [ip for ip in ips if "region" in ip]

with open('data/event_names.json', 'r') as event_names_file:
    event_names = [json.loads(line) for line in event_names_file.readlines()]

def emitJoins():
    joins = [user 
        for _, user in all_users.items()
        if user.next_event.join  < datetime.now() and (not user.next_event.join_published)
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

def get_random_event():
    event_ids = list(all_events.keys())
    return all_events[event_ids[random.randint(0, len(event_ids)-1)]]

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
        name = fake.name()
        uuid = fake.uuid4()
        start = datetime.now() + timedelta(seconds=random.randint(0, max_start_delay))
        all_events[uuid] = Event(
            id=uuid, 
            start=start,
            end = start + timedelta(seconds=random.randint(min_event_length, max_event_length))
        )

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

    reactor.run()

if __name__ == '__main__':
    run_loop()