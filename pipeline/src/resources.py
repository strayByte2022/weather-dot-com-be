from dagster import ConfigurableResource, InitResourceContext
from confluent_kafka import Producer
import requests
from .hdfs_writer import HDFSWriter
from hdfs import InsecureClient


class OpenWeatherResource(ConfigurableResource):
    api_key: str
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, lat: float, lon: float) -> dict:
        url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


class KafkaProducerResource(ConfigurableResource):
    bootstrap_servers: str
    topic: str

    def setup_for_execution(self, context: InitResourceContext):
        self._producer = Producer(
            {"bootstrap.servers": self.bootstrap_servers})

    def send_message(self, data):
        self._producer.produce(self.topic, data)
        self._producer.flush()


class HDFSWriterResource(ConfigurableResource):
    hdfs_url: str
    user: str
    base_path: str
    namespace: str = None  # Optional, default is None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        # Instantiate the HDFS client
        if self.namespace:
            client = InsecureClient(
                self.hdfs_url, user=self.user, root=self.namespace)
        else:
            client = InsecureClient(self.hdfs_url, user=self.user)

        self._hdfs_writer = HDFSWriter(
            client=client,
            base_path=self.base_path,
            namespace=self.namespace
        )

    def append(self, partition_key: str, data: str) -> None:
        """
        Append data to a partitioned file in HDFS.

        Args:
            partition_key: The partition key for the file
            data: The data to append to the file
        """
        self._hdfs_writer.append(partition_key, data)
