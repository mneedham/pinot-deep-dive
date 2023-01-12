# Demo

```
During this session we will do a deep dive into Apache Pinot.
We'll learn about batch and real-time data ingestion and how Pinot supports queries of tables containing data loaded by both methods.
We'll also explore the way that Pinot stores data and the impact of different indexing strategies.
Finally, we'll look at some features introduced in recent versions of Pinot, including ingesting from SQL, pausing/resuming real-time ingestion, and data de-duplication. 
```

## Streaming data

```bash
tea +python.org python loop.py --help
```

```
tea +python.org python loop.py --users 10000
```

```bash
tea +python.org python loop.py --users 1000 --events 100 --max-start-delay 0 --min-event-length 60 --max-event-length 180
```

## Kafka

```bash
docker exec -it kafka-deep-dive kafka-topics.sh \
  --bootstrap-server localhost:9093 \
  --create \
  --topic events \
  --partitions 5
```

(Delete Topic)

```bash
docker exec -it kafka-deep-dive kafka-topics.sh \
  --bootstrap-server localhost:9093 \
  --delete \
  --topic events
```

Ingest events

```bash
tea +python.org python loop.py --users 10000 --events 1000 --max-start-delay 0 --min-event-length 60 --max-event-length 120 | 
jq -cr --arg sep 😊 '[.eventId, tostring] | join($sep)' | 
kcat -P -b localhost:9092 -t events -K😊
```

Check data going into each partition

```bash
docker exec -it kafka-deep-dive kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list localhost:9093 \
  --topic events
```

Query the streams

```bash
kcat -C -b localhost:9092 -t events
```

## Pinot 

Show the schema and table config first

Schema:

```
pygmentize pinot/config/schema.json
```

* Column types
* Data types
* Mapping from source data to columns

Table Config

```
pygmentize pinot/config/table.json
```

* Table type
* Segment config
* Stream config
* Segment flush thresholds (https://dev.startree.ai/docs/pinot/recipes/configuring-segment-threshold)

```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   apachepinot/pinot:0.11.0-SNAPSHOT-a6f5e89-20230110-arm64  AddTable \
     -schemaFile /config/schema.json \
     -tableConfigFile /config/table.json \
     -controllerHost "pinot-controller-deep-dive" \
    -exec
```

Go to http://localhost:9000/

```sql
select count(*) filter(WHERE action = 'Join') AS joinEvents,
       count(*) filter(WHERE action = 'Leave') AS leaveEvents
from events 
limit 10
```

Go to http://localhost:9000/#/tenants/table/events_REALTIME

* Explain the naming pattern for segments (<table>__<partitionId>__<incrementingCount>__<ts>)
* Select an individual segment
  ** Consuming vs Consumed  
  ** REST API - Show how we can force a segment to flush?
  ** Deep store for consumed segments (`ls -alh deep-store/events`)

Explain the forward index (slides)

Timestamp index

Querying the timestamp field:


```sql
select datetrunc('SECOND', ts) as tsMinute, count(*) 
from events 
WHERE tsMinute > fromDateTime('2022-01-09', 'yyyy-MM-dd') 
group by tsMinute
order by count(*) DESC
limit 10
```

```
pygmentize pinot/config/table-timestamp-index.json
```

* Apply the index and then reload the segments
* Show the new derived columns (search for `$ts`)

### Offline data import

Add the offline table

Same schema, but show the table config

```bash
pygmentize pinot/config/table-offline-timestamp-index.json
```

```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   apachepinot/pinot:0.11.0-SNAPSHOT-a6f5e89-20230110-arm64 AddTable \
     -schemaFile /config/schema.json \
     -tableConfigFile /config/table-offline-timestamp-index.json \
     -controllerHost "pinot-controller-deep-dive" \
     -update \
    -exec  
```

Import the data:

```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   -v $PWD/deep-store:/deep-store \
   -v $PWD/batch-data:/batch-data \
   apachepinot/pinot:0.11.0-SNAPSHOT-a6f5e89-20230110-arm64 LaunchDataIngestionJob \
     -jobSpecFile /config/job-spec.yml \
     -values PINOT_CONTROLLER="pinot-controller-deep-dive"
```

```sql
SET taskName = 'events-task5';
SET input.fs.className = 'org.apache.pinot.spi.filesystem.LocalPinotFS';
SET includeFileNamePattern='glob:**/*.json';
INSERT INTO events
FROM FILE 'file:///batch-data/';
```

Query both tables:

```sql
select $segmentName, count(*)
from events
group by $segmentName
limit 100
```

Time boundaries (https://dev.startree.ai/docs/pinot/concepts/time-boundary)

```bash
pygmentize boundary.py
```

```bash
tea +python.org python boundary.py
```

### Upserts

https://docs.pinot.apache.org/basics/data-import/upsert

```bash
pygmentize pinot/config/schema-upserts.json
```

```bash
pygmentize pinot/config/table-upserts.json
```


```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   apachepinot/pinot:0.11.0-SNAPSHOT-a6f5e89-20230110-arm64  AddTable \
     -schemaFile /config/schema-upserts.json \
     -tableConfigFile /config/table-upserts.json \
     -controllerHost "pinot-controller-deep-dive" \
    -exec
```

Sub in appropriate values:

```sql
select * 
from events_upserts 
where eventId = 'd15fc074-317e-4ad2-8cb7-36f3587c304b'
AND userId = '341813b5-b00b-4bba-83ac-65db95260483'
limit 10
--option(skipUpsert=true)
```

### Dedup

https://docs.pinot.apache.org/basics/data-import/dedup


```bash
pygmentize pinot/config/schema-dedup.json
```

```bash
pygmentize pinot/config/table-dedup.json
```

```bash
docker run \
   --network deep-dive \
   -v $PWD/pinot/config:/config \
   apachepinot/pinot:0.11.0-SNAPSHOT-a6f5e89-20230110-arm64  AddTable \
     -schemaFile /config/schema-dedup.json \
     -tableConfigFile /config/table-dedup.json \
     -controllerHost "pinot-controller-deep-dive" \
    -exec
```

```sql
select userId, name, count(*) 
from events_dedup 
GROUP BY userId, name
ORDER BY count(*) DESC
limit 10
```

```sql
select userId, name, count(*) 
from events
GROUP BY userId, name
ORDER BY count(*) DESC
limit 10
```