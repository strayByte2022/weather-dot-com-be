#!/bin/bash
echo "Waiting for Kafka brokers to be ready..."
sleep 5


topic_exists() {
  opt/kafka/bin/kafka-topics.sh --bootstrap-server $1:19092 --list | grep "^$2$" > /dev/null
  return $?
}

ensure() {
  BROKER=$1
  TOPIC_NAME=$2
  
  if ! topic_exists $BROKER $TOPIC_NAME; then
    echo "Creating topic '$TOPIC_NAME'..."
    opt/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER:19092 --create --topic $TOPIC_NAME --partitions 3 --replication-factor 1
  else
    echo "Topic '$TOPIC_NAME' already exists, skipping creation."
  fi
}

ensure broker-1 weather_raw_topic
ensure broker-1 weather_10min_avg