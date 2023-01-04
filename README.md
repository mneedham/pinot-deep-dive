# Pinot Deep Dive

The instructions below assume that you're using the https://github.com/teaxyz/cli[tea.xyz^] package manager.

## Install dependencies

```bash
tea +python.org pip install -r requirements.txt
```

## Generate IP addresses / Lat Longs

If you want to generate your own, you'll need to first get a token from https://ipinfo.io.



```
while true; do tea +python.org python ips.py >> data/ips.json; done
```