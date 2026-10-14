"""
Database pipeline — loads processed JSON files into PostgreSQL
and updates pipeline watermarks after successful loads.
"""
import logging
from loaders.postgres import PostgresLoader
from watermarks import WatermarkManager

logger = logging.getLogger(__name__)


def load_processed_data(weather_result: dict | None = None):
    logger.info("Starting PostgreSQL loading...")

    loader = PostgresLoader()
    watermark = WatermarkManager()

    try:
        # Economic indicators
        economic_path = (
            "/app/data/processed/worldbank/"
            "world_bank_clean.json"
        )
        economic_inserted = loader.load_economic_indicators(
            economic_path
        )
        logger.info(
            "Economic records inserted: %d", economic_inserted
        )
        if economic_inserted == 0:
            logger.warning(
                "No economic records inserted — "
                "data may already be current."
            )

        # Weather
        weather_inserted = 0

        if weather_result and not weather_result.get("skipped"):
            weather_path = weather_result["processed_path"]

            weather_inserted = loader.load_daily_weather(
                weather_path
            )
            logger.info(
                "Weather records inserted: %d", weather_inserted
            )
            if weather_inserted == 0:
                logger.warning(
                    "No weather records inserted — "
                    "data may already be current."
                )

            # Update watermark only after confirmed DB load
            from datetime import date
            watermark.set_last_date(
                pipeline_name="weather",
                loaded_date=date.fromisoformat(
                    weather_result["end_date"]
                ),
                records_loaded=weather_inserted,
            )
        else:
            logger.info("Weather fetch was skipped, no watermark update.")

        return {
            "economic_inserted": economic_inserted,
            "weather_inserted": weather_inserted,
        }

    finally:
        loader.close()
        watermark.close()
