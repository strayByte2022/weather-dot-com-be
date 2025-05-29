import asyncio
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaProducer

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "weather-data"

# Default coordinates (London)
DEFAULT_LAT = 51.5073219
DEFAULT_LON = -0.1276474

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

async def fetch_current_weather(lat=DEFAULT_LAT, lon=DEFAULT_LON):
    """Fetch current weather data from OpenWeatherMap API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "units": "metric",
                    "appid": API_KEY
                }
            )
            
            if response.status_code == 200:
                weather_data = response.json()
                
                # Add timestamp
                weather_data["fetched_at"] = datetime.now().isoformat()
                
                # Send to Kafka
                producer.send(TOPIC, weather_data)
                producer.flush()
                
                # Log the data
                city_name = weather_data.get("name", "Unknown")
                temp = weather_data.get("main", {}).get("temp", "N/A")
                description = weather_data.get("weather", [{}])[0].get("description", "N/A")
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Weather data fetched for {city_name}: {temp}°C, {description}")
                
                return weather_data
            else:
                print(f"Error fetching weather data: HTTP {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None

async def weather_scheduler():
    """Main scheduler that fetches weather data every minute"""
    print("Weather scheduler started. Fetching weather data every 60 seconds...")
    print(f"Target location: Lat {DEFAULT_LAT}, Lon {DEFAULT_LON}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            await fetch_current_weather()
            # Wait for 60 seconds (1 minute)
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("\nWeather scheduler stopped by user.")
    except Exception as e:
        print(f"Weather scheduler error: {str(e)}")
    finally:
        producer.close()
        print("Kafka producer closed.")

if __name__ == "__main__":
    # Check if required environment variables are set
    if not API_KEY:
        print("Error: API_KEY environment variable is not set")
        exit(1)
    
    if not BASE_URL:
        print("Error: BASE_URL environment variable is not set")
        exit(1)
    
    # Run the scheduler
    asyncio.run(weather_scheduler())