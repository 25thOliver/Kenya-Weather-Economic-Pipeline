SELECT
    country_code,
    country,
    indicator_code,
    year,
    value
FROM {{ source('postgres', 'economic_indicators') }}