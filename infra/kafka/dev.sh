#!/bin/bash

set -e

cd ~/kafka_2.13-4.3.1

if [[ ! -f ~/.init ]]; then
    KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
    bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c /app/infra/kafka/server.properties
    touch ~/.init
fi

exec bin/kafka-server-start.sh /app/infra/kafka/server.properties