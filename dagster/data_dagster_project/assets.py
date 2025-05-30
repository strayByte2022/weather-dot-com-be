from dagster import asset, StaticPartitionsDefinition, io_manager

from .io_manager import KafkaIOManager

CITY_PARTITIONS = StaticPartitionsDefinition(["new_york", "london", "tokyo"])

@io_manager
def kafka_io_manager(init_context):
    producer_config = init_context.resource_config["producer_config"]
    topic = init_context.resource_config["topic"]
    return KafkaIOManager(producer_config, topic)

@asset(name='weather_data', partitions_def=CITY_PARTITIONS, io_manager_key='kafka_io_manager')
def weather_data(context):
    city = context.partition_key
    import requests
    lat = 10.7754189
    lon = 106.6639836
    start = 1710759827
    end = 1730759827
    url = f"https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={API_KEY}"
    response = requests.get(url)
    return response.json()
