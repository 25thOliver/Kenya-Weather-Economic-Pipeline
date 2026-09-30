SELECT
    date,
    location,
    COUNT(*) AS record_count
FROM {{ ref('stg_daily_weather') }}
GROUP BY
    date,
    location
HAVING COUNT(*) > 1