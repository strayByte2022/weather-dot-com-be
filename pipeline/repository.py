from dagster import repository
from jobs import weather_job, weather_schedule

@repository
def weather_repo():
    return [weather_job, weather_schedule]