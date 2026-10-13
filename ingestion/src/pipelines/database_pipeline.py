import logging
from loaders.postgres import PostgresLoader

logger = logging.getLogger(__name__)


def load_processed_data():
    logger.info("Starting PostgreSQL loading...")

    loader = PostgresLoader()

    try:
        economic_path = (
            "/app/data/processed/worldbank/"
            "world_bank_clean.json"
        )

        weather_path = (
            "/app/data/processed/weather/"
            "weather_daily.json"
        )

        economic_inserted = loader.load_economic_indicators(
            economic_path
        )
        logger.info("Economic records inserted: %d", economic_inserted)

        weather_inserted = loader.load_daily_weather(weather_path)
        logger.info("Weather records inserted: %d", weather_inserted)

        if economic_inserted == 0:
            logger.warning(
                "No economic records inserted — "
                "all rows may already exist or data may be empty."
            )

        if weather_inserted == 0:
            logger.warning(
                "No weather records inserted — "
                "all rows may already exist or data may be empty."
            )

        return {
            "economic_inserted": economic_inserted,
            "weather_inserted": weather_inserted,
        }

    finally:
        loader.close()
