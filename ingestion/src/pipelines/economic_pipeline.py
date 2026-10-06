from clients.world_bank import WorldBankClient
from transformers.world_bank import transform_world_bank


def run_economic_pipeline(config, storage):
    economic_config = config["economic"]

    indicator_codes = [
        indicator["code"]
        for indicator in economic_config["indicators"]
    ]

    print("Starting World Bank Pipeline...")
    print(
        f"Country: "
        f"{economic_config['country_code']}"
    )
    print(
        f"Indicators: {len(indicator_codes)}"
    )

    client = WorldBankClient(
        base_url=economic_config["base_url"],
        country_code=economic_config["country_code"],
    )

    data = client.fetch_indicators(
        indicator_codes
    )

    records = data["records"]

    print(
        f"Records received: {len(records)}"
    )

    raw_path = client.save_raw(
        data,
        "/app/data/raw/worldbank",
    )


    print(f"Raw data saved to: {raw_path}")

    object_key = (
        f"worldbank/{raw_path.name}"
    )

    storage_path = storage.upload_file(
        str(raw_path),
        object_key,
    )

    processed_path = (
        "/app/data/processed/worldbank/"
        "world_bank_clean.json"
    )


    transform_world_bank(
        str(raw_path),
        processed_path,
    )

    print(
        f"Processed data saved to: "
        f"{processed_path}"
    )

    return processed_path
