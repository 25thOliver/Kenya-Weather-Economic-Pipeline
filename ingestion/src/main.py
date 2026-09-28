from pathlib import Path

import yaml

from clients.world_bank import WorldBankClient

def load_config():
    config_path = Path("config/sources.yml")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def main():
    config = load_config()

    economic_config = config["economic"]

    indicator_codes = [
        indicator["code"]
        for indicator in economic_config["indicators"]
    ]

    print("Starting World Bank ingestion...")
    print(f"Country: {economic_config['country_code']}")
    print(f"Indicators: {len(indicator_codes)}")


    client = WorldBankClient(
        base_url=economic_config["base_url"],
        country_code=economic_config["country_code"],
    )

    data = client.fetch_indicators(indicator_codes)

    records = data["records"]

    print(f"Records received: {len(records)}")

    output_path = client.save_raw(
        data,
        "data/raw/worldbank",
    )

    print(f"Raw data saved to: {output_path}")


if __name__ == "__main__":
    main()