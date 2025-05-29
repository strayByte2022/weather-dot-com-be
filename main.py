from fastapi import FastAPI
from data.weather import CurrentWeatherResponse, HistoricalWeatherResponse
import httpx
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime, timedelta

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

@app.get("/weather")
async def get_weather(lat: float = 51.5073219, lon: float = -0.1276474):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}data/2.5/weather",
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
async def get_weather_history(lat: float = 51.5073219, lon: float = -0.1276474):
    try:
        # Calculate timestamps for 24 hours ago and current time
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(hours=24)).timestamp())

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
