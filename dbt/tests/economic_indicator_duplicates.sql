SELECT
    country_code,
    indicator_code,
    year,
    COUNT(*) AS record_count
FROM {{ ref('stg_economic_indicators') }}
GROUP BY
    country_code,
    indicator_code,
    year
HAVING COUNT(*) > 1