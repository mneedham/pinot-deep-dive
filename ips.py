from faker import Faker
import requests
import json
import os

access_token = os.environ.get("ACCESS_TOKEN", None)

if not access_token:
    raise Exception("Can't generate any IP addresses/Lat Longs without an access token. You can get one for free from https://ipinfo.io")


fake = Faker()

try:
    ip = fake.ipv4_public()
    response = requests.get(f"https://ipinfo.io/{ip}?token={access_token}")

    print(json.dumps(
        response.json()
    ))
except Exception as e:
    pass