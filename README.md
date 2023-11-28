# schema_registry
Test default values and aliases on AVRO schemas.

The purpose of this demo is:
 - How to use default values on an AVRO schemas
 - How `aliases` work on AVRO schemas
 - Show how a consumer deserialise messages based on the `schema_id` set on each serialised message (bytes 1 to 4) and how to ignore that by setting a fixed schema on the schema deserialiser

Requirements:
 - Python +3.8
 - Install requirements: `python3 -m pip install -r requirements.txt`

Demo:
 - Start docker compose: `docker-compose up -d`
 - Wait one minute and create six subject/schemas: `./create_schema.sh` (BACKWARD compatibility)
   - Six schemas will be created across two subjects (`topic_1-value` and `topic_2-value`)
   - See files at folder `schemas/`
   - Output example:
```
Creating schema 'schemas/topic_1.v1.json' (Subject: topic_1-value)
 - Done: SchemaID #1 created

Creating schema 'schemas/topic_1.v2.json' (Subject: topic_1-value)
 - Done: SchemaID #2 created

Creating schema 'schemas/topic_1.v3.json' (Subject: topic_1-value)
 - Done: SchemaID #3 created

Creating schema 'schemas/topic_1.v4.json' (Subject: topic_1-value)
 - Done: SchemaID #4 created

Creating schema 'schemas/topic_2.v1.json' (Subject: topic_2-value)
 - Done: SchemaID #5 created

Creating schema 'schemas/topic_2.v2.json' (Subject: topic_2-value)
 - Done: SchemaID #6 created
```
 - Produce data to Kafka: `python3 producer.py`
   - Data will be produced to the two topics (`topic_1` and `topic_2`)
   - Either as `{"field_1": "some_uuid"}` or `{"new_field_1": "some_uuid"}` depending on the schema version it needs to publish to, no other field will be set on the payload
   - Output example:
```
Producing user records to Kafka.
Topic: topic_1
 - SchemaID: 1
 - Original: {'field_1': 'f24b1ac11db3468c8fac300c8b8f403f'}
 - Serialised: b'\x00\x00\x00\x00\x01@f24b1ac11db3468c8fac300c8b8f403f'
-----------------------------------

Topic: topic_1
 - SchemaID: 2
 - Original: {'field_1': '0f58acbd778d4f7f880f32f20a17f0fa'}
 - Serialised: b'\x00\x00\x00\x00\x02@0f58acbd778d4f7f880f32f20a17f0fa:Field #2 on schema version #2'
-----------------------------------

Topic: topic_1
 - SchemaID: 3
 - Original: {'field_1': 'c1b5ca51f10f4e4c9ba50722fd71c99b'}
 - Serialised: b'\x00\x00\x00\x00\x03@c1b5ca51f10f4e4c9ba50722fd71c99b:Field #2 on schema version #3:Field #3 on schema version #3'
-----------------------------------

Topic: topic_1
 - SchemaID: 4
 - Original: {'new_field_1': '96ffb880bcd340a78622f8481071e34c'}
 - Serialised: b'\x00\x00\x00\x00\x04@96ffb880bcd340a78622f8481071e34cBNew Field #2 on schema version #4BNew Field #3 on schema version #4BNew Field #4 on schema version #4'
-----------------------------------

Topic: topic_2
 - SchemaID: 5
 - Original: {'field_1': '10bce781486b49f5828924e3bbf1db79'}
 - Serialised: b'\x00\x00\x00\x00\x05@10bce781486b49f5828924e3bbf1db79'
-----------------------------------

Topic: topic_2
 - SchemaID: 6
 - Original: {'new_field_1': '944ed154c4f44cf4b8a107b05e66d27b'}
 - Serialised: b'\x00\x00\x00\x00\x06@944ed154c4f44cf4b8a107b05e66d27b'
-----------------------------------
```
 - Go to the Confluent Control Center and see the schemas on the two topics created: http://localhost:9021
 - Consume data from Kafka (deserialising the messages as per `schema_id` set on each message): `python3 consumer.py`
   - As no schema was set on the avro deserialiser, the messages will be deserialised as per `schema_id` set on the messages (bytes 1 to 4)
   - Output example:
```
Topic: topic_2
 - SchemaID: 5
 - Serialised: b'\x00\x00\x00\x00\x05@10bce781486b49f5828924e3bbf1db79'
 - Deserialised: {'field_1': '10bce781486b49f5828924e3bbf1db79'}
-----------------------------------

Topic: topic_2
 - SchemaID: 6
 - Serialised: b'\x00\x00\x00\x00\x06@944ed154c4f44cf4b8a107b05e66d27b'
 - Deserialised: {'new_field_1': '944ed154c4f44cf4b8a107b05e66d27b'}
-----------------------------------

Topic: topic_1
 - SchemaID: 1
 - Serialised: b'\x00\x00\x00\x00\x01@f24b1ac11db3468c8fac300c8b8f403f'
 - Deserialised: {'field_1': 'f24b1ac11db3468c8fac300c8b8f403f'}
-----------------------------------

Topic: topic_1
 - SchemaID: 2
 - Serialised: b'\x00\x00\x00\x00\x02@0f58acbd778d4f7f880f32f20a17f0fa:Field #2 on schema version #2'
 - Deserialised: {'field_1': '0f58acbd778d4f7f880f32f20a17f0fa', 'field_2': 'Field #2 on schema version #2'}
-----------------------------------

Topic: topic_1
 - SchemaID: 3
 - Serialised: b'\x00\x00\x00\x00\x03@c1b5ca51f10f4e4c9ba50722fd71c99b:Field #2 on schema version #3:Field #3 on schema version #3'
 - Deserialised: {'field_1': 'c1b5ca51f10f4e4c9ba50722fd71c99b', 'field_2': 'Field #2 on schema version #3', 'field_3': 'Field #3 on schema version #3'}
-----------------------------------

Topic: topic_1
 - SchemaID: 4
 - Serialised: b'\x00\x00\x00\x00\x04@96ffb880bcd340a78622f8481071e34cBNew Field #2 on schema version #4BNew Field #3 on schema version #4BNew Field #4 on schema version #4'
 - Deserialised: {'new_field_1': '96ffb880bcd340a78622f8481071e34c', 'new_field_2': 'New Field #2 on schema version #4', 'new_field_3': 'New Field #3 on schema version #4', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------
```
 - Close the consumer by pressing (CTRL-C)
 - Consume data from Kafka (overidding schema_id on `topic_1`): `python3 consumer.py -t1 schemas/topic_1.v4.json`
   - As the schema `schemas/topic_1.v4.json` was set on the avro deserialiser, it will ignore the `schema_id` set on the messages (bytes 1 to 4) and use that schema to deserialise the messages
   - See below how the `topic_1` messages differs from the ones above. As that schema uses an alias it will deserialise as `field_n` but the field name on the deserialised message is `new_field_n`
   - Output example:
```
Topic: topic_2
 - SchemaID: 5
 - Serialised: b'\x00\x00\x00\x00\x05@10bce781486b49f5828924e3bbf1db79'
 - Deserialised: {'field_1': '10bce781486b49f5828924e3bbf1db79'}
-----------------------------------

Topic: topic_2
 - SchemaID: 6
 - Serialised: b'\x00\x00\x00\x00\x06@944ed154c4f44cf4b8a107b05e66d27b'
 - Deserialised: {'new_field_1': '944ed154c4f44cf4b8a107b05e66d27b'}
-----------------------------------

Topic: topic_1
 - SchemaID: 1
 - Serialised: b'\x00\x00\x00\x00\x01@f24b1ac11db3468c8fac300c8b8f403f'
 - Deserialised: {'new_field_1': 'f24b1ac11db3468c8fac300c8b8f403f', 'new_field_2': 'New Field #2 on schema version #4', 'new_field_3': 'New Field #3 on schema version #4', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------

Topic: topic_1
 - SchemaID: 2
 - Serialised: b'\x00\x00\x00\x00\x02@0f58acbd778d4f7f880f32f20a17f0fa:Field #2 on schema version #2'
 - Deserialised: {'new_field_1': '0f58acbd778d4f7f880f32f20a17f0fa', 'new_field_2': 'Field #2 on schema version #2', 'new_field_3': 'New Field #3 on schema version #4', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------

Topic: topic_1
 - SchemaID: 3
 - Serialised: b'\x00\x00\x00\x00\x03@c1b5ca51f10f4e4c9ba50722fd71c99b:Field #2 on schema version #3:Field #3 on schema version #3'
 - Deserialised: {'new_field_1': 'c1b5ca51f10f4e4c9ba50722fd71c99b', 'new_field_2': 'Field #2 on schema version #3', 'new_field_3': 'Field #3 on schema version #3', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------

Topic: topic_1
 - SchemaID: 4
 - Serialised: b'\x00\x00\x00\x00\x04@96ffb880bcd340a78622f8481071e34cBNew Field #2 on schema version #4BNew Field #3 on schema version #4BNew Field #4 on schema version #4'
 - Deserialised: {'new_field_1': '96ffb880bcd340a78622f8481071e34c', 'new_field_2': 'New Field #2 on schema version #4', 'new_field_3': 'New Field #3 on schema version #4', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------
```
 - Close the consumer by pressing (CTRL-C)
 - Consume data from Kafka (overidding schema_id on `topic_2`): `python3 consumer.py -t2 schemas/topic_2.v2.json`
   - As the schema `schemas/topic_2.v2.json` was set on the avro deserialiser, it will ignore the `schema_id` set on the messages (bytes 1 to 4) and use that schema to deserialise the messages
   - See below how the `topic_2` messages differs from the ones above. As that schema uses an alias it will deserialise as `field_n` but the field name on the deserialised message is `new_field_n`
   - Output example:
```
Topic: topic_2
 - SchemaID: 5
 - Serialised: b'\x00\x00\x00\x00\x05@10bce781486b49f5828924e3bbf1db79'
 - Deserialised: {'new_field_1': '10bce781486b49f5828924e3bbf1db79'}
-----------------------------------

Topic: topic_2
 - SchemaID: 6
 - Serialised: b'\x00\x00\x00\x00\x06@944ed154c4f44cf4b8a107b05e66d27b'
 - Deserialised: {'new_field_1': '944ed154c4f44cf4b8a107b05e66d27b'}
-----------------------------------

Topic: topic_1
 - SchemaID: 1
 - Serialised: b'\x00\x00\x00\x00\x01@f24b1ac11db3468c8fac300c8b8f403f'
 - Deserialised: {'field_1': 'f24b1ac11db3468c8fac300c8b8f403f'}
-----------------------------------

Topic: topic_1
 - SchemaID: 2
 - Serialised: b'\x00\x00\x00\x00\x02@0f58acbd778d4f7f880f32f20a17f0fa:Field #2 on schema version #2'
 - Deserialised: {'field_1': '0f58acbd778d4f7f880f32f20a17f0fa', 'field_2': 'Field #2 on schema version #2'}
-----------------------------------

Topic: topic_1
 - SchemaID: 3
 - Serialised: b'\x00\x00\x00\x00\x03@c1b5ca51f10f4e4c9ba50722fd71c99b:Field #2 on schema version #3:Field #3 on schema version #3'
 - Deserialised: {'field_1': 'c1b5ca51f10f4e4c9ba50722fd71c99b', 'field_2': 'Field #2 on schema version #3', 'field_3': 'Field #3 on schema version #3'}
-----------------------------------

Topic: topic_1
 - SchemaID: 4
 - Serialised: b'\x00\x00\x00\x00\x04@96ffb880bcd340a78622f8481071e34cBNew Field #2 on schema version #4BNew Field #3 on schema version #4BNew Field #4 on schema version #4'
 - Deserialised: {'new_field_1': '96ffb880bcd340a78622f8481071e34c', 'new_field_2': 'New Field #2 on schema version #4', 'new_field_3': 'New Field #3 on schema version #4', 'new_field_4': 'New Field #4 on schema version #4'}
-----------------------------------
```

To stop de demo:
 - Close the consumer by pressing (CTRL-C)
 - Stop docker compose: `docker-compose down`

In summary:
 - `aliases` should be used when renaming fields for both producers and consumers
 - Using `aliases` only for the consumers (or a particular consumer) can be complex to manage as the target consumer(s) would need to ignore the `schema_id` and deserialise the messages as per a given schema (which won't likely be in the schema registry under the subject otherwise it will impact the producers as they would need to produce data using the new field names)
