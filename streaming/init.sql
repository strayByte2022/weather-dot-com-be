{
  "ksql": "
    CREATE STREAM weather_raw_stream (
      coord STRUCT<lon DOUBLE, lat DOUBLE>,
      weather ARRAY<STRUCT<id INT, main VARCHAR, description VARCHAR, icon VARCHAR>>,
      main STRUCT<temp DOUBLE, feels_like DOUBLE, temp_min DOUBLE, temp_max DOUBLE,
                  pressure INT, humidity INT, sea_level INT, grnd_level INT>,
      visibility INT,
      wind STRUCT<speed DOUBLE, deg INT, gust DOUBLE>,
      rain STRUCT<`1h` DOUBLE>,
      clouds STRUCT<\"all\" INT>,
      dt BIGINT,
      sys STRUCT<type INT, id INT, country VARCHAR, sunrise BIGINT, sunset BIGINT>
    ) WITH (
      KAFKA_TOPIC='weather_raw_topic',
      VALUE_FORMAT='JSON'
    );

    CREATE STREAM weather_flat_stream AS
    SELECT
      'global-key'            AS global_key,
      main->temp              AS main_temp,
      main->feels_like        AS main_feels_like,
      main->temp_min          AS main_temp_min,
      main->temp_max          AS main_temp_max,
      main->pressure          AS main_pressure,
      main->humidity          AS main_humidity,
      weather[0]->main        AS weather_main,
      weather[0]->description AS weather_description,
      visibility,
      wind->speed             AS wind_speed,
      wind->deg               AS wind_deg,
      wind->gust              AS wind_gust,
      rain->`1h`              AS rain_1h,
      clouds->\"all\"         AS clouds_all,
      dt,
      sys->sunrise            AS sys_sunrise,
      sys->sunset             AS sys_sunset
    FROM weather_raw_stream;

  CREATE TABLE weather_10min_avg
    WITH (KAFKA_TOPIC='weather_10min_avg', VALUE_FORMAT='JSON') AS
  SELECT
    'global-key' AS global_key,
    AVG(main_temp) AS avg_temp,
    AVG(main_pressure) AS avg_pressure,
    AVG(main_humidity) AS avg_humidity,
    AVG(wind_speed) AS avg_wind_speed
  FROM weather_flat_stream
  WINDOW TUMBLING (SIZE 10 MINUTES)
  GROUP BY 'global-key';  -- use a dummy key for single-partition stats
  ",
  "streamsProperties": {
    "ksql.streams.auto.offset.reset": "earliest"
  }
}
