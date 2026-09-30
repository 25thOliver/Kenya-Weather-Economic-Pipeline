SELECT
    date,
    location,
    temperature_avg,
    temperature_min,
    temperature_max,
    rainfall,
    humidity_avg,
    wind_speed_avg
FROM {{ source('postgres', 'daily_weather') }}