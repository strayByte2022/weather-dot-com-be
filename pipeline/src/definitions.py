from dagster import (
    AssetExecutionContext,
    asset,
    Definitions,
    EnvVar,
    StaticPartitionsDefinition,
    define_asset_job,
    schedule,
    RunRequest,
    DefaultScheduleStatus
)
import json
from .resources import OpenWeatherResource, KafkaProducerResource, HDFSWriterResource
from datetime import datetime
from dotenv import load_dotenv
from .locations import get_location_keys

load_dotenv()


# Define locations as static partitions
weather_locations = StaticPartitionsDefinition(get_location_keys())


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
    context.log.info(
        f"Sending weather data for {weather_data.get('name', 'unknown')} to Kafka")

    # Serialize and send to Kafka
    kafka.send_message(json.dumps(weather_data).encode("utf-8"))

    return {"status": "sent", "location": context.partition_key}


@asset(
    partitions_def=weather_locations,
    compute_kind="hadoop",
    group_name="weather",
    deps=["weather_data"]
)
def weather_hadoop(context: AssetExecutionContext, hdfs_writer: HDFSWriterResource, weather_data):
    """Store weather data in HDFS partitioned by location."""
    location = context.partition_key
    context.log.info(f"Writing weather data for location {location} to HDFS")

    # Convert weather data to string format (JSON)
    data_str = json.dumps(weather_data) + "\n"

    # Use the partition key (location) to organize data in HDFS
    hdfs_writer.append(partition_key=location, data=data_str)

    return {
        "status": "stored",
        "location": location,
        "timestamp": datetime.now().isoformat()
    }


# Define a job that materializes all partitions
weather_all_locations_job = define_asset_job(
    name="weather_all_locations_job",
    selection=["weather_data", "weather_kafka", "weather_hadoop"],
)


# Create a schedule to run every minute
@schedule(
    name="weather_minute_schedule",
    cron_schedule="*/5 * * * *",
    job=weather_all_locations_job,
    execution_timezone="UTC",
    default_status=DefaultScheduleStatus.RUNNING
)
def weather_schedule():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    for location in weather_locations.get_partition_keys():
        yield RunRequest(
            partition_key=location,
            run_key=f"{location}_{current_time}"
        )


defs = Definitions(
    assets=[weather_data, weather_kafka, weather_hadoop],
    resources={
        "openweather": OpenWeatherResource(
            api_key=EnvVar("OPENWEATHER_API_KEY")
        ),
        "kafka": KafkaProducerResource(
            bootstrap_servers=EnvVar("KAFKA_BOOTSTRAP_SERVERS"),
            topic=EnvVar("KAFKA_TOPIC_WEATHER")
        ), "hdfs_writer": HDFSWriterResource(
            hdfs_url=EnvVar("HDFS_URL"),
            user=EnvVar("HDFS_USER"),
            base_path=EnvVar("HDFS_BASE_PATH")
        )
    },
    schedules=[weather_schedule],
)
