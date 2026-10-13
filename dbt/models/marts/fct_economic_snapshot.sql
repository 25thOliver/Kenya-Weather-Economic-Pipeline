/*
  fct_economic_snapshot — World Bank annual economic indicators for Kenya.
  Adds year-over-year percentage change per indicator.
  One row per indicator per year.
*/

WITH base AS (
    SELECT
        year,
        year_date,
        indicator_code,
        value
    FROM {{ ref('stg_economic_indicators') }}
    WHERE value IS NOT NULL
)

SELECT
    year,
    year_date,
    indicator_code,

    -- Human-readable indicator names
    CASE indicator_code
        WHEN 'NY.GDP.MKTP.CD'   THEN 'GDP (Current USD)'
        WHEN 'NY.GDP.MKTP.KD.ZG'THEN 'GDP Growth Rate (%)'
        WHEN 'SP.POP.TOTL'      THEN 'Total Population'
        WHEN 'FP.CPI.TOTL'      THEN 'Consumer Price Index'
        WHEN 'SL.UEM.TOTL.ZS'   THEN 'Unemployment Rate (%)'
        WHEN 'NV.AGR.TOTL.ZS'   THEN 'Agriculture (% of GDP)'
        WHEN 'EG.ELC.ACCS.ZS'   THEN 'Electricity Access (%)'
        WHEN 'IT.NET.USER.ZS'   THEN 'Internet Users (%)'
        ELSE indicator_code
    END                                                 AS indicator_name,

    value,

    -- Year-over-year change
    LAG(value) OVER (
        PARTITION BY indicator_code
        ORDER BY year
    )                                                   AS prev_year_value,

    ROUND(
        (
            (value - LAG(value) OVER (
                PARTITION BY indicator_code ORDER BY year
            ))
            / NULLIF(
                ABS(LAG(value) OVER (
                    PARTITION BY indicator_code ORDER BY year
                )),
                0
            )
        ) * 100,
        2
    )                                                   AS yoy_change_pct

FROM base
ORDER BY indicator_code, year
