import json
import hashlib
import argparse

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python simple Avro COnsumer")
    parser.add_argument(
        "-t1",
        dest="t1_schema",
        type=str,
        help=f"Schema file name for the 'topic_1'",
        default=None,
    )
    parser.add_argument(
        "-t2",
        dest="t2_schema",
        type=str,
        help=f"Schema file name for the 'topic_2'",
        default=None,
    )
    args = parser.parse_args()

    # Schema Registry client
    schema_registry_conf = {
        "url": "http://localhost:8081",
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Schema registry avro deserialisers
    topics = ["topic_1", "topic_2"]
    avro_deserializer = dict()
    for n, schema in enumerate([args.t1_schema, args.t2_schema]):
        if schema is None:
            schema_str = None
        else:
            schema_str = json.dumps(json.loads(open(schema, "r").read()))
        avro_deserializer[topics[n]] = AvroDeserializer(
            schema_registry_client,
            schema_str=schema_str,  # if this is set to the actual schema string it will ignore the Schema_ID on each serialised message
        )

    # Kafka Producer client
    consumer_conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": f"group-01-{hashlib.md5(f'{args.t1_schema}_{args.t2_schema}'.encode()).hexdigest()}",
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe(topics)

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is not None:
                deserialised_value = avro_deserializer[msg.topic()](
                    msg.value(),
                    SerializationContext(
                        msg.topic(),
                        MessageField.VALUE,
                    ),
                )
                print(f"Topic: {msg.topic()}")
                print(f" - SchemaID: {int.from_bytes(msg.value()[1:5])}")
                print(f" - Serialised: {msg.value()}")
                print(f" - Deserialised: {deserialised_value}")
                print("-----------------------------------\n")
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(f"<<<ERROR: {err}>>>")
            print(f"Topic: {msg.topic()}")
            print(f" - SchemaID: {int.from_bytes(msg.value()[1:5])}")
            print(f" - Serialised: {msg.value()}")
            print("-----------------------------------\n")

    consumer.close()
