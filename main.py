from fastapi import FastAPI, Query
from data.weather import CurrentWeatherResponse, HistoricalWeatherResponse
import httpx
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime, timedelta
from data.enums.date_range import RangeOption
from kafka import KafkaConsumer
import json
import threading
import time
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
HISTORY_URL = os.getenv("HISTORY_URL")

# Global variable to store latest weather data from Kafka
latest_weather_data = None
data_lock = threading.Lock()

# Kafka consumer for background data collection
def kafka_consumer_thread():
    global latest_weather_data
    consumer = KafkaConsumer(
        "weather-data",
        bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092"),
        auto_offset_reset='latest',  # Only get new messages
        enable_auto_commit=True,
        group_id='api-weather-consumers',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print("API Kafka consumer started - listening for weather data...")
    
    for message in consumer:
        try:
            with data_lock:
                latest_weather_data = {
                    'data': message.value,
                    'timestamp': datetime.now().isoformat(),
                    'kafka_metadata': {
                        'partition': message.partition,
                        'offset': message.offset
                    }
                }
            print(f"API received weather update for {message.value.get('name', 'Unknown')}")
        except Exception as e:
            print(f"Error processing Kafka message in API: {str(e)}")

# Start Kafka consumer in background thread
consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
consumer_thread.start()
@app.get("/weather/stream")
async def get_weather():
    """Get current weather data from Kafka stream"""
    try:
        with data_lock:
            if latest_weather_data is None:
                return JSONResponse(
                    content={
                        "error": "No weather data available yet. Please wait for the scheduler to provide data.",
                        "message": "Weather data is fetched every minute by the scheduler."
                    }, 
                    status_code=503
                )
            
            # Return the latest weather data with additional metadata
            response_data = {
                "weather_data": latest_weather_data['data'],
                "api_metadata": {
                    "data_source": "kafka_stream",
                    "last_updated": latest_weather_data['timestamp'],
                    "kafka_partition": latest_weather_data['kafka_metadata']['partition'],
                    "kafka_offset": latest_weather_data['kafka_metadata']['offset']
                }
            }
            
            return JSONResponse(content=response_data)
            
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/weather/direct")
async def get_weather_direct(lat: float = 51.5073219, lon: float = -0.1276474):
    """Get weather data directly from OpenWeatherMap API (fallback endpoint)"""
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
            weather_data = response.json()
            return JSONResponse(content=weather_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/weather/history")
async def get_weather_history(lat: float = 51.5073219, lon: float = -0.1276474, range: RangeOption = Query(default=RangeOption.one_day, description="Choose from 1, 3, or 30 days")):
    try:
        
        now = datetime.now()
        days = int(range.value)
        start_time = int((now - timedelta(days=days)).timestamp())
        end_time = int(now.timestamp())

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://history.openweathermap.org/data/2.5/history/city",
                params={
                    "lat": lat,
                    "lon": lon,
                    "type": "hour",
                    "start": start_time,
                    "end": end_time,
                    "units": "metric",
                    "appid": API_KEY
                }
            )
            history_data = response.json()
            return JSONResponse(content=history_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


