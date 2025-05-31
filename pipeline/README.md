### Requirement

- Python >= 3.8
- Pip
- ~9GB of RAM available

### Setup .env file

```shell
OPENWEATHER_API_KEY=""
KAFKA_BOOTSTRAP_SERVERS="localhost:29092,localhost:39092,localhost:49092"
KAFKA_TOPIC_WEATHER="weather_raw_topic"
DAGSTER_HOME="/storage"
```

### Start venv

```shell
py -m venv venv

Windows machine
.\venv\Scripts\activate
or
POSIX machine
./venv/bin/activate
```

### Set Dagster home

```shell
Powershell
$env:DAGSTER_HOME = "$PWD\storage"
or
Bash
export DAGSTER_HOME="$PWD/storage"
or
set DAGSTER_HOME="<dir>\weather-dot-com-be\pipeline\storage"
```

### Install dependencies and environment

From inside the virtual environment

```shell
pip install -e ".[dev]"
docker compose up -d
```

### Run Dagster

```shell
cd pipeline

dagster dev
http://127.0.0.1:3000
```

```shell
./kafka-console-consumer.sh --bootstrap-server broker-1:19092,broker-2:19092,broker-3:19092 --topic weather_raw_topic --from-beginning

./kafka-console-consumer.sh --bootstrap-server broker-1:19092,broker-2:19092,broker-3:19092 --topic weather_10min_avg --from-beginning
```
