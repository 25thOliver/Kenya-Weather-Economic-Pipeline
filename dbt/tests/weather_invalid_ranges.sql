SELECT *
FROM {{ ref('stg_daily_weather') }}
WHERE humidity_avg < 0
   OR humidity_avg > 100
   OR rainfall < 0
   OR wind_speed_avg < 0