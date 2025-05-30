from dagster import ConfigurableResource, InitResourceContext
from confluent_kafka import Producer
import requests

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
        self._producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        
    def send_message(self, data):
        self._producer.produce(self.topic, data)
        self._producer.flush()