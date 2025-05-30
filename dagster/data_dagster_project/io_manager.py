import json
from typing import Any

from confluent_kafka import Producer
from dagster import InputContext, OutputContext, IOManager


class KafkaIOManager(IOManager):
    def __init__(self, producer_config, topic):
        # These values will be populated by Dagster resource system
        self._producer = None

        if producer_config is not None:
            self.producer_config = producer_config
        if topic is not None:
            self.topic = topic

        super().__init__()

    def _get_producer(self):
        if self._producer is None:
            self._producer = Producer(self.producer_config)
        return self._producer

    def handle_output(self, context: OutputContext, obj: Any) -> None:
        producer = self._get_producer()
        serialized_data = json.dumps(obj).encode('utf-8')

        producer.produce(
            topic=self.topic,
            key=context.partition_key.encode('utf-8') if hasattr(context, 'partition_key') else None,
            value=serialized_data
        )
        producer.flush(5)

    def load_input(self, context: InputContext) -> Any:
        return None
        # raise NotImplementedError("Reading from Kafka is not supported")


# if __name__ == "__main__":
#     kafka_instance = ConfigurableKafkaIOManager(producer_config={'bootstrap.servers': 'localhost:9092'}, topic='weather_data')
#     kafka_io_manager = kafka_instance.create_io_manager(None)
