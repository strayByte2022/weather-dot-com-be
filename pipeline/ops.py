from dagster import op
import json
import requests

@op(required_resource_keys={"openweather_client"})
def fetch_weather_for_partition(context) -> dict:
    """
    Fetch current weather for a lat/lon partition.
    """
    client = context.resources.openweather_client
    
    # Parse partition key to get lat/lon
    SPILT_PARTITION_KEY = " "
    partition_key = context.op_execution_context.partition_key
    lat, lon = map(float, partition_key.split(SPILT_PARTITION_KEY))
    
    url = (
        f"{client['base_url']}?lat={lat}&lon={lon}&appid={client['api_key']}"
    )
    
    context.log.info(f"Fetching weather for location: lat={lat}, lon={lon}")
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    # Add location info to the data for downstream processing
    data["location"] = {"lat": lat, "lon": lon}
    
    return data

@op(required_resource_keys={"kafka_producer"})
def send_to_kafka(context, data: dict):
    """
    Publish fetched data to Kafka.
    """
    producer = context.resources.kafka_producer["producer"]
    topic = context.resources.kafka_producer["topic"]
    
    # Add timestamp to track when data was collected
    data["collected_at"] = context.get_current_time().timestamp()
    
    context.log.info(f"Sending weather data for {data['name']} to Kafka")
    producer.produce(topic, json.dumps(data).encode("utf-8"))
    producer.flush()