from dagster import graph, ScheduleDefinition, static_partitioned_config
from ops import fetch_weather_for_partition, send_to_kafka
from resources import openweather_client, kafka_producer

WEATHER_LOCATIONS = [
    "40.7128 -74.0060",  # New York
    "34.0522 -118.2437",  # Los Angeles
    "41.8781 -87.6298",   # Chicago
    "29.7604 -95.3698",   # Houston
    "33.4484 -112.0740",  # Phoenix
    # Add more lat/lon pairs as needed
]

@static_partitioned_config(partition_keys=WEATHER_LOCATIONS)
def weather_location_config(partition_key: str):
    return {"ops": {"fetch_weather_for_partition": {"config": {"location": partition_key}}}}

@graph
def weather_graph():
    weather_data = fetch_weather_for_partition()
    send_to_kafka(weather_data)


weather_job = weather_graph.to_job(
    name="weather_job",
    resource_defs={
        "openweather_client": openweather_client.configured({
            "api_key": "your_openweather_api_key",
            "lat_lon_file": "path/to/lat_lon.json"
        }),
        "kafka_producer": kafka_producer.configured({
            "bootstrap_servers": "localhost:29092,localhost:39092,localhost:49092",
            "topic": "weather_data"
        }),
    },
    config=weather_location_config
)

# Schedule: every minute
weather_schedule = ScheduleDefinition(
    job=weather_job,
    cron_schedule="* * * * *",
    execution_timezone="UTC",
)