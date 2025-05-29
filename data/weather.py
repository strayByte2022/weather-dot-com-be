class Coord:
    lon: float
    lat: float

class WeatherAttribute:
    id: int
    main: str
    description: str
    icon: str

class Weather:
    WeatherAttributes: list[WeatherAttribute]

class Main:
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: float
    humidity: float
    sea_level: float
    grnd_level: float
class Wind:
    speed: float
    deg: float
    gust: float
class Rain:
    one_h: float
    three_h: float

class Clouds:
    all: int

class Sys:
    type: int
    id: int
    country: str
    sunrise: int
    sunset: int


class HistoricalWeatherData:
    dt: int
    main: Main
    wind: Wind
    clouds: Clouds
    weather: list[WeatherAttribute]

class HistoricalWeatherResponse:
    message: str
    cod: str
    city_id: int
    calctime: float
    cnt: int
    list: list[HistoricalWeatherData]

class CurrentWeatherResponse:
    coord: Coord
    weather: list[Weather]
    base: str
    main: Main
    visibility: int
    wind: Wind
    rain: Rain
    clouds: Clouds
    dt: int
    sys: Sys
    timezone: int
    id: int
    name: str
    cod: int