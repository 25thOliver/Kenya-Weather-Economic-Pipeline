/*
  fct_daily_climate — enriched daily weather fact table.
  Joins weather observations with location dimension,
  adds derived columns useful for dashboards.
*/

SELECT
    w.date,
    w.location,
    l.latitude,
    l.longitude,
    l.county,
    l.region,

    -- Temperature
    w.temperature_avg,
    w.temperature_min,
    w.temperature_max,
    ROUND(
        (w.temperature_max - w.temperature_min)::numeric,
        2
    )                                           AS temperature_range,

    -- Precipitation
    w.rainfall,
    CASE
        WHEN w.rainfall >= 10 THEN 'heavy'
        WHEN w.rainfall >= 1  THEN 'moderate'
        WHEN w.rainfall >  0  THEN 'light'
        ELSE                       'dry'
    END                                         AS rainfall_category,

    -- Humidity & Wind
    w.humidity_avg,
    w.wind_speed_avg,

    -- Time spine (useful for Superset time-series)
    DATE_TRUNC('month', w.date)::date           AS month,
    DATE_TRUNC('year',  w.date)::date           AS year,
    EXTRACT(DOW FROM w.date)::int               AS day_of_week

FROM {{ ref('stg_daily_weather') }} w
LEFT JOIN {{ ref('dim_location') }} l
    ON w.location = l.location
