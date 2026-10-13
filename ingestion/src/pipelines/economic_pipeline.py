import logging
from clients.world_bank import WorldBankClient
from transformers.world_bank import transform_world_bank

logger = logging.getLogger(__name__)


def run_economic_pipeline(config, storage):
    economic_config = config["economic"]

    indicator_codes = [
        indicator["code"]
        for indicator in economic_config["indicators"]
    ]

    logger.info("Starting World Bank pipeline...")
    logger.info("Country: %s", economic_config["country_code"])
    logger.info("Indicators: %d", len(indicator_codes))

    client = WorldBankClient(
        base_url=economic_config["base_url"],
        country_code=economic_config["country_code"],
    )

    data = client.fetch_indicators(indicator_codes)
    records = data["records"]

    logger.info("Total records received: %d", len(records))

    raw_path = client.save_raw(
        data,
        "/app/data/raw/worldbank",
    )

    logger.info("Raw data saved to: %s", raw_path)

    object_key = f"worldbank/{raw_path.name}"

    storage_path = storage.upload_file(
        str(raw_path),
        object_key,
    )

    logger.info("Uploaded to MinIO: %s", storage_path)

    processed_path = (
        "/app/data/processed/worldbank/"
        "world_bank_clean.json"
    )

    transform_world_bank(str(raw_path), processed_path)

    logger.info("Processed data saved to: %s", processed_path)

    return processed_path
