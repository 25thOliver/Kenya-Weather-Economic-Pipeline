CREATE TABLE IF NOT EXISTS economic_indicators (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    country VARCHAR(100) NOT NULL,
    indicator_code VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    value DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS daily_weather (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    temperature_avg DOUBLE PRECISION,
    temperature_min DOUBLE PRECISION,
    temperature_max DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    humidity_avg DOUBLE PRECISION,
    wind_speed_avg DOUBLE PRECISION
);