#!/bin/sh

echo "Waiting for kafka..."

while ! kafkacat -b $KAFKA_INSTANCE -L; do
    sleep 0.1
done

echo "Kafka started"

exec "$@"