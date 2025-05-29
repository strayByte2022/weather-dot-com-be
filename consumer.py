from kafka import KafkaConsumer
import json
from datetime import datetime

consumer = KafkaConsumer(
    "weather-data",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='weather-consumers',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("=== Weather Data Consumer Started ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Bootstrap servers: localhost:9092")
print(f"Topic: weather-data")
print(f"Consumer group: weather-consumers")
print("Listening for weather data...\n")

for message in consumer:
    try:
        data = message.value
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract weather information
        city_name = data.get('name', 'Unknown')
        country = data.get('sys', {}).get('country', 'Unknown')
        temp = data.get('main', {}).get('temp', 'N/A')
        feels_like = data.get('main', {}).get('feels_like', 'N/A')
        humidity = data.get('main', {}).get('humidity', 'N/A')
        pressure = data.get('main', {}).get('pressure', 'N/A')
        weather_desc = data.get('weather', [{}])[0].get('description', 'N/A')
        wind_speed = data.get('wind', {}).get('speed', 'N/A')
        
        # Message metadata
        partition = message.partition
        offset = message.offset
        
        print(f"[{timestamp}] === NEW WEATHER MESSAGE ===")
        print(f"Kafka Metadata: Partition={partition}, Offset={offset}")
        print(f"Location: {city_name}, {country}")
        print(f"Temperature: {temp}°C (feels like {feels_like}°C)")
        print(f"Weather: {weather_desc}")
        print(f"Humidity: {humidity}%, Pressure: {pressure} hPa")
        print(f"Wind Speed: {wind_speed} m/s")
        
        # Check if fetched_at timestamp exists (from scheduler)
        if 'fetched_at' in data:
            print(f"Data fetched at: {data['fetched_at']}")
        
        print(f"Raw message size: {len(json.dumps(data))} bytes")
        print("-" * 50)
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR processing message: {str(e)}")
        print(f"Raw message: {message.value}")
        print("-" * 50)
