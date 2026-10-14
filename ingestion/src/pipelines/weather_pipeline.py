"""
Weather pipeline — fetches Open-Meteo hourly data for Kenyan cities,
aggregates to daily records, saves raw JSON to MinIO, and writes
processed JSON ready for database loading.

Uses a watermark to fetch only new data since the last successful run.
"""
import logging
from datetime import date, timedelta

from clients.open_meteo import OpenMeteoClient
from pipeline_transformers.weather import transform_weather

logger = logging.getLogger(__name__)

# How far back to start on the very first run (no watermark yet)
WEATHER_DEFAULT_START = date(2024, 1, 1)

# Open-Meteo archive data lags by ~5 days; stay safely behind today
ARCHIVE_LAG_DAYS = 5


def run_weather_pipeline(config, storage, watermark_manager=None):
    weather_config = config["weather"]

    client = OpenMeteoClient(
        base_url=weather_config["base_url"],
        timezone_name=weather_config["timezone"],
    )

    variables = weather_config["variables"]

    # Compute date window
    end_date = date.today() - timedelta(days=ARCHIVE_LAG_DAYS)

    if watermark_manager is not None:
        last_date = watermark_manager.get_last_date(
            "weather",
            default=WEATHER_DEFAULT_START,
        )
        start_date = last_date + timedelta(days=1)
    else:
        start_date = WEATHER_DEFAULT_START

    if start_date > end_date:
        logger.info(
            "Weather data is already up to date "
            "(watermark: %s, safe end: %s). Skipping fetch.",
            start_date - timedelta(days=1),
            end_date,
        )
        return {
            "processed_path": None,
            "end_date": str(end_date),
            "skipped": True,
        }
    # ------------------------------------------------------------------

    logger.info("Starting Open-Meteo pipeline...")
    logger.info("Locations: %d", len(weather_config["locations"]))
    logger.info("Variables: %d", len(variables))
    logger.info(
        "Date range: %s to %s",
        start_date.isoformat(),
        end_date.isoformat(),
    )

    results = []

    for location in weather_config["locations"]:
        name = location["name"]
        logger.info("Fetching %s...", name)

        result = client.fetch_location(
            name=name,
            latitude=location["latitude"],
            longitude=location["longitude"],
            variables=variables,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        results.append(result)

        timestamps = (
            result["data"].get("hourly", {}).get("time", [])
        )
        logger.info("  %s: %d hourly records", name, len(timestamps))

    raw_path = client.save_raw(
        results,
        "/app/data/raw/open-meteo",
    )
    logger.info("Raw weather data saved to: %s", raw_path)

    object_key = f"open-meteo/{raw_path.name}"
    storage_path = storage.upload_file(str(raw_path), object_key)
    logger.info("Uploaded to MinIO: %s", storage_path)

    processed_path = (
        "/app/data/processed/weather/weather_daily.json"
    )

    transform_weather(str(raw_path), processed_path)
    logger.info("Processed data saved to: %s", processed_path)

    return {
        "processed_path": processed_path,
        "end_date": end_date.isoformat(),
        "skipped": False,
    }
