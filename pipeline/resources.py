import os
from dotenv import load_dotenv
from dagster import resource
from confluent_kafka import Producer

load_dotenv()

@resource(config_schema={"api_key": str, "lat_lon_file": str})
def openweather_client(init_context):
    """
    Resource to call the OpenWeather History API.
    Expects:
      api_key: your OPENWEATHER_API_KEY
      lat_lon_file: path to JSON file containing list of {lat, lon}
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not set in .env file.")

    return {
        "api_key": api_key,
        "base_url": "https://api.openweathermap.org/data/2.5/weather",
    }

@resource(config_schema={"bootstrap_servers": str, "topic": str})
def kafka_producer(init_context):
    """
    Resource for Kafka Producer.
    Expects:
      bootstrap_servers: e.g., "localhost:9092"
      topic: Kafka topic to produce messages
    """
    producer = Producer({"bootstrap.servers": init_context.resource_config["bootstrap_servers"]})
    return {"producer": producer, "topic": init_context.resource_config["topic"]}