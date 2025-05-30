from dagster import (
    AssetExecutionContext,
    asset, 
    Definitions, 
    EnvVar, 
    StaticPartitionsDefinition,
    define_asset_job,
    schedule,
    RunRequest,
)
import json
from .resources import OpenWeatherResource, KafkaProducerResource
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# Define locations as static partitions
weather_locations = StaticPartitionsDefinition([
    "40.7128 -74.0060",  # New York
    "34.0522 -118.2437",  # Los Angeles
    "41.8781 -87.6298",   # Chicago
    "29.7604 -95.3698",   # Houston
    "33.4484 -112.0740",  # Phoenix
])

@asset(
    partitions_def=weather_locations,
    compute_kind="python",
    group_name="weather",
)
def weather_data(context: AssetExecutionContext, openweather: OpenWeatherResource) -> dict:
    """Fetch current weather for a specific location partition."""
    # Get the current partition (location)
    partition_key = context.partition_key
    lat, lon = map(float, partition_key.split(" "))
    
    context.log.info(f"Fetching weather for location: lat={lat}, lon={lon}")
    
    # Get weather data
    data = openweather.get_weather(lat, lon)
    
    # Add location info to the data
    data["location"] = {"lat": lat, "lon": lon}
    data["collected_at"] = datetime.now().strftime("%H:%M:%S")
    
    return data

@asset(
    partitions_def=weather_locations,
    compute_kind="kafka",
    group_name="weather",
    deps=["weather_data"]
)
def weather_kafka(context: AssetExecutionContext, kafka: KafkaProducerResource, weather_data):
    """Send weather data to Kafka."""
    context.log.info(f"Sending weather data for {weather_data.get('name', 'unknown')} to Kafka")
    
    # Serialize and send to Kafka
    kafka.send_message(json.dumps(weather_data).encode("utf-8"))
    
    return {"status": "sent", "location": context.partition_key}

# Define a job that materializes all partitions
weather_all_locations_job = define_asset_job(
    name="weather_all_locations_job",
    selection=["weather_data", "weather_kafka"],
)

# Create a schedule to run every minute
@schedule(
    name="weather_minute_schedule",
    cron_schedule="* * * * *",
    job=weather_all_locations_job,
    execution_timezone="UTC",
)
def weather_schedule():
    for location in weather_locations.get_partition_keys():
        yield RunRequest(partition_key=location)

defs = Definitions(
    assets=[weather_data, weather_kafka],
    resources={
        "openweather": OpenWeatherResource(
            api_key=EnvVar("OPENWEATHER_API_KEY")
        ),
        "kafka": KafkaProducerResource(
            bootstrap_servers=EnvVar("KAFKA_BOOTSTRAP_SERVERS"),
            topic=EnvVar("KAFKA_TOPIC_WEATHER")
        ),
    },
    schedules=[weather_schedule],
)