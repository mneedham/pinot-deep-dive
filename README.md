# Pinot Deep Dive

The instructions below assume that you're using the https://github.com/teaxyz/cli[tea.xyz^] package manager.

## Install dependencies

```bash
tea +python.org pip install -r requirements.txt
```

## Generate IP addresses / Lat Longs

If you want to generate your own, you'll need to first get a token from https://ipinfo.io.
Then run the following:

```bash
while true; do tea +python.org python ips.py >> data/ips.json; done
```

## Generate events

```bash
tea +python.org python loop.py --users 10000
```

or with Docker:

```bash
docker build -t event-loop:0.0.1 .
docker run -it -v $PWD/data:/usr/src/app/data event-loop:0.0.1 python loop.py
```

```bash
docker run -it -v $PWD/data:/usr/src/app/data event-loop:0.0.1 python loop.py --users 1000 --events 100 | 
jq -cr --arg sep 😊 '[.eventId, tostring] | join($sep)' | 
kcat -P -b localhost:9092 -t events -K😊
```

```bash
kcat -C -b localhost:9092 -t events -f 'Key: %k, payload: %s\n'
```

```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   apachepinot/pinot:0.11.0-arm64 AddTable \
     -schemaFile /config/schema.json \
     -tableConfigFile /config/table.json \
     -controllerHost "pinot-controller-deep-dive" \
    -exec  
```

## Actions

We'll have the following actions: Join, Leave, Like, Dislike

https://schema.org/Action