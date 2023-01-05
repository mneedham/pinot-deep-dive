import requests
import json

response = requests.get("https://story-shack-cdn-v2.glitch.me/generators/event-name-generator")

print(json.dumps(
    response.json()["data"]
))