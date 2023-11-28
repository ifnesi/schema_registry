#!/bin/bash
echo
for schema in schemas/*.json
do
    subject=`echo $schema | cut -d'/' -f 2 | cut -d'.' -f 1`
    echo "Creating schema '$schema' (Subject: $subject-value)"
    SCHEMA_ID=$(echo '{"schemaType": "'AVRO'", "schema": "'$(cat $schema | jq -c . | sed 's/"/\\"/g')'"}' | curl -1 -s http://localhost:8081/subjects/$subject-value/versions \
    -H "Expect:" \
    -H "Accept: application/vnd.schemaregistry.v1+json, application/vnd.schemaregistry+json, application/json" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d @- | jq .id)
    echo " - Done: SchemaID #$SCHEMA_ID created"
    echo
done