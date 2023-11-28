import os
import glob
import json

from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


if __name__ == "__main__":
    schema_files = sorted(glob.glob(os.path.join("schemas", "*")))

    # Schema Registry client
    schema_registry_conf = {
        "url": "http://localhost:8081",
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Schema registry avro serialisers (1:1 to each schema)
    avro_serializer = list()
    topic_field_map = dict()
    for file in schema_files:
        with open(file, "r") as f:
            schema = f.read()
            schema_json = json.loads(schema)
            avro_serializer.append(
                AvroSerializer(
                    schema_registry_client,
                    json.dumps(schema_json),
                )
            )
            topic_field_map[file] = schema_json["fields"][0]["name"]

    # Kafka Producer client
    producer_conf = {
        "bootstrap.servers": "localhost:9092",
    }
    producer = Producer(producer_conf)

    print("Producing user records to Kafka")
    producer.poll(0.0)
    for n, file in enumerate(schema_files):
        try:
            topic = os.path.splitext(os.path.splitext(os.path.split(file)[-1])[0])[0]
            value = {
                topic_field_map[file]: uuid4().hex,
            }
            value_serialised = avro_serializer[n](
                value,
                SerializationContext(
                    topic,
                    MessageField.VALUE,
                ),
            )
            print(f"Topic: {topic}")
            print(f" - SchemaID: {int.from_bytes(value_serialised[1:5])}")
            print(f" - Original: {value}")
            print(f" - Serialised: {value_serialised}")
            print("-----------------------------------\n")
            producer.produce(
                topic=topic,
                value=value_serialised,
            )
        except ValueError as err:
            print(f"Invalid input ({err}), discarding record")

    print("\nFlushing records...")
    producer.flush()
