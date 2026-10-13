import logging
from clients.open_meteo import OpenMeteoClient
from pipeline_transformers.weather import transform_weather

logger = logging.getLogger(__name__)


def run_weather_pipeline(config, storage):
    weather_config = config["weather"]

    client = OpenMeteoClient(
        base_url=weather_config["base_url"],
        timezone_name=weather_config["timezone"],
    )

    variables = weather_config["variables"]
    start_date = "2025-01-01"
    end_date = "2025-12-31"

    logger.info("Starting Open-Meteo pipeline...")
    logger.info("Locations: %d", len(weather_config["locations"]))
    logger.info("Variables: %d", len(variables))
    logger.info("Date range: %s to %s", start_date, end_date)

    results = []

    for location in weather_config["locations"]:
        name = location["name"]
        logger.info("Fetching %s...", name)

        result = client.fetch_location(
            name=name,
            latitude=location["latitude"],
            longitude=location["longitude"],
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )

        results.append(result)

        timestamps = result["data"].get("hourly", {}).get("time", [])
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
        "/app/data/processed/weather/"
        "weather_daily.json"
    )

    transform_weather(str(raw_path), processed_path)

    logger.info("Processed data saved to: %s", processed_path)

    return processed_path
