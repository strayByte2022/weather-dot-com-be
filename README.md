# OpenWeather Backend - Distributed Weather Data System

A distributed weather data system built with FastAPI, Kafka, and OpenWeatherMap API. This system implements an event-driven architecture where weather data is continuously fetched, streamed through Kafka, and consumed by multiple services.

## 🏗️ Architecture Overview

```
Weather Scheduler → Kafka Topic → Consumer (Debug Output)
                              ↘ API Background Consumer → REST API Endpoints
```

### Components

1. **Weather Scheduler** (`weather_scheduler.py`) - Fetches weather data every minute
2. **Kafka Message Broker** - Streams weather data between services
3. **Consumer** (`consumer.py`) - Processes and displays weather data with debugging info
4. **REST API** (`main.py`) - Serves weather data from Kafka stream

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for Kafka)
- OpenWeatherMap API Key

### Installation

1. **Clone and setup environment:**
   ```bash
   cd openweather-be
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file:
   ```env
   API_KEY=your_openweathermap_api_key
   BASE_URL=http://api.openweathermap.org
   HISTORY_URL=https://history.openweathermap.org
   KAFKA_BROKER=localhost:9092
   ```

3. **Start Kafka services:**
   ```bash
   docker-compose up -d
   ```

4. **Start the system components:**
   
   **Terminal 1 - Weather Scheduler:**
   ```bash
   python weather_scheduler.py
   # Or use: start_weather_scheduler.bat
   ```
   
   **Terminal 2 - Consumer (Optional - for debugging):**
   ```bash
   python consumer.py
   ```
   
   **Terminal 3 - API Server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Get Current Weather (from Kafka Stream)

**GET** `/weather/stream`

Returns the latest weather data from the Kafka stream (updated every minute by the scheduler).

**Response:**
```json
{
  "weather_data": {
    "coord": {"lon": -0.1276, "lat": 51.5073},
    "weather": [
      {
        "id": 803,
        "main": "Clouds",
        "description": "broken clouds",
        "icon": "04d"
      }
    ],
    "main": {
      "temp": 23.88,
      "feels_like": 24.12,
      "temp_min": 22.25,
      "temp_max": 25.43,
      "pressure": 1013,
      "humidity": 64
    },
    "wind": {"speed": 3.6, "deg": 250},
    "name": "London",
    "sys": {"country": "GB"},
    "fetched_at": "2025-05-29T23:15:30.123456"
  },
  "api_metadata": {
    "data_source": "kafka_stream",
    "last_updated": "2025-05-29T23:15:35.789012",
    "kafka_partition": 0,
    "kafka_offset": 42
  }
}
```

**Error Response (503):**
```json
{
  "error": "No weather data available yet. Please wait for the scheduler to provide data.",
  "message": "Weather data is fetched every minute by the scheduler."
}
```

#### 2. Get Weather Direct (from OpenWeatherMap API)

**GET** `/weather/direct`

Fetches weather data directly from OpenWeatherMap API (fallback endpoint).

**Query Parameters:**
- `lat` (float, optional): Latitude (default: 51.5073219 - London)
- `lon` (float, optional): Longitude (default: -0.1276474 - London)

**Example:**
```bash
curl "http://localhost:8000/weather/direct?lat=40.7128&lon=-74.0060"
```

**Response:**
```json
{
  "coord": {"lon": -0.1276, "lat": 51.5073},
  "weather": [
    {
      "id": 803,
      "main": "Clouds",
      "description": "broken clouds",
      "icon": "04d"
    }
  ],
  "main": {
    "temp": 23.88,
    "feels_like": 24.12,
    "temp_min": 22.25,
    "temp_max": 25.43,
    "pressure": 1013,
    "humidity": 64
  },
  "wind": {"speed": 3.6, "deg": 250},
  "name": "London",
  "sys": {"country": "GB"}
}
```

#### 3. Get Weather History

**GET** `/weather/history`

Retrieves historical weather data for a specified time range.

**Query Parameters:**
- `lat` (float, optional): Latitude (default: 51.5073219)
- `lon` (float, optional): Longitude (default: -0.1276474)
- `range` (enum, optional): Time range - `one_day`, `three_days`, or `thirty_days` (default: `one_day`)

**Example:**
```bash
curl "http://localhost:8000/weather/history?range=three_days"
```

**Response:**
```json
{
  "list": [
    {
      "dt": 1640995200,
      "main": {
        "temp": 15.23,
        "pressure": 1013,
        "humidity": 78
      },
      "weather": [
        {
          "main": "Rain",
          "description": "light rain"
        }
      ]
    }
    // ... more historical data
  ]
}
```

## 🔧 System Components

### Weather Scheduler (`weather_scheduler.py`)

**Purpose:** Automatically fetches weather data every 60 seconds and sends it to Kafka.

**Features:**
- Configurable location (default: London)
- Automatic retry on API failures
- Detailed logging with timestamps
- Graceful shutdown with Ctrl+C

**Usage:**
```bash
python weather_scheduler.py
```

**Output:**
```
Weather scheduler started. Fetching weather data every 60 seconds...
Target location: Lat 51.5073219, Lon -0.1276474
Press Ctrl+C to stop

[2025-05-29 23:15:30] Weather data fetched for London: 23.88°C, broken clouds
[2025-05-29 23:16:30] Weather data fetched for London: 23.85°C, broken clouds
```

### Consumer (`consumer.py`)

**Purpose:** Consumes weather data from Kafka and displays detailed debugging information.

**Features:**
- Comprehensive weather data display
- Kafka message metadata (partition, offset)
- Message size reporting
- Error handling and logging
- Timestamp tracking

**Usage:**
```bash
python consumer.py
```

**Output:**
```
=== Weather Data Consumer Started ===
Timestamp: 2025-05-29 23:15:30
Bootstrap servers: localhost:9092
Topic: weather-data
Consumer group: weather-consumers
Listening for weather data...

[2025-05-29 23:15:30] === NEW WEATHER MESSAGE ===
Kafka Metadata: Partition=0, Offset=42
Location: London, GB
Temperature: 23.88°C (feels like 24.12°C)
Weather: broken clouds
Humidity: 64%, Pressure: 1013 hPa
Wind Speed: 3.6 m/s
Data fetched at: 2025-05-29T23:15:30.123456
Raw message size: 1247 bytes
--------------------------------------------------
```

### REST API (`main.py`)

**Purpose:** Serves weather data through HTTP endpoints, consuming from Kafka stream.

**Features:**
- Background Kafka consumer thread
- Thread-safe data storage
- Multiple data sources (Kafka stream + direct API)
- Comprehensive error handling
- CORS support

## 🐳 Docker Services

The `docker-compose.yml` includes:

- **Zookeeper**: Kafka coordination service
- **Kafka**: Message broker (port 9092)
- **Kafka UI**: Web interface for Kafka management (port 8080)

**Kafka UI Access:**
```
http://localhost:8080
```

## 📁 Project Structure

```
openweather-be/
├── main.py                     # FastAPI application
├── weather_scheduler.py        # Weather data scheduler
├── consumer.py                 # Kafka consumer with debugging
├── start_weather_scheduler.bat # Windows batch script
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Kafka services
├── .env                        # Environment variables
├── data/
│   ├── weather.py             # Weather data models
│   └── enums/
│       └── date_range.py      # Date range enumerations
└── README.md                   # This file
```

## 🔍 Monitoring and Debugging

### Kafka Topic Monitoring

1. **Kafka UI**: http://localhost:8080
2. **Consumer Groups**: Monitor `weather-consumers` and `api-weather-consumers`
3. **Topic**: `weather-data`

### Logs and Debugging

- **Scheduler**: Shows fetch timestamps and weather summaries
- **Consumer**: Detailed weather data and Kafka metadata
- **API**: Background consumer status and request logs

### Health Checks

- **API Health**: `GET /weather/stream` should return recent data
- **Kafka Health**: Consumer should show new messages every minute
- **Scheduler Health**: Should log successful fetches every 60 seconds

## 🛠️ Development

### Adding New Endpoints

1. Add endpoint to `main.py`
2. Update this README documentation
3. Test with the provided `test_main.http` file

### Modifying Weather Data

1. Update models in `data/weather.py`
2. Modify scheduler logic in `weather_scheduler.py`
3. Update consumer display in `consumer.py`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `API_KEY` | OpenWeatherMap API key | Required |
| `BASE_URL` | OpenWeatherMap base URL | `http://api.openweathermap.org` |
| `HISTORY_URL` | Historical data URL | `https://history.openweathermap.org` |
| `KAFKA_BROKER` | Kafka broker address | `localhost:9092` |

## 🚨 Troubleshooting

### Common Issues

1. **"No weather data available yet"**
   - Ensure weather scheduler is running
   - Check Kafka services are up
   - Verify API key is valid

2. **Kafka connection errors**
   - Start Docker services: `docker-compose up -d`
   - Check port 9092 is available
   - Verify KAFKA_BROKER environment variable

3. **API key errors**
   - Verify API_KEY in .env file
   - Check OpenWeatherMap account status
   - Ensure API key has required permissions

### Stopping Services

```bash
# Stop all Python processes
Ctrl+C in each terminal

# Stop Kafka services
docker-compose down
```

## 📄 License

This project is for educational purposes and demonstrates distributed systems concepts using Kafka and FastAPI.