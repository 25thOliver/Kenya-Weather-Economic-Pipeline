SELECT
    country_code,
    country,
    indicator_code,
    year,
    MAKE_DATE(year, 1, 1) AS year_date,
    value
FROM {{ source('postgres', 'economic_indicators') }}