from pathlib import Path

import yaml

from clients.world_bank import WorldBankClient
from clients.open_meteo import OpenMeteoClient

def load_config():
    config_path = Path("config/sources.yml")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def ingest_world_bank(config):
    economic_config = config["economic"]

    indicator_codes = [
        indicator["code"]
        for indicator in economic_config["indicators"]
    ]

    print("Starting World Banking ingestion...")
    print(f"Country: {economic_config['country_code']}")
    print(f"Indicators: {len(indicator_codes)}")

    client = WorldBankClient(
        base_url=economic_config["base_url"],
        country_code=economic_config["countyr_code"],
    )

    data = client.fetch_indicators(
        indicator_codes
    )

    records = data["records"]

    print(f"Records received: {len(records)}")

    output_path = client.save_raw(
        data,
        "data/raw/worldbank",
    )

    print(f"Raw data saved to: {output_path}")


def ingest_open_meteo(config):
    weather_config = config["weather"]

    client = OpenMeteoClient(
        base_url=weather_config["base_url"],
        timezone_name=weather_config["timezone"],
    )

    variables = weather_config["variables"]

    # Initial development/test window
    start_date = "2025-01-01"
    end_date = "2025-01-07"

    results = []

    print()
    print("Starting Open-Meteo ingestion...")
    print(f"Locations: {len(weather_config['locations'])}")
    print(f"Variables: {len(variables)}")
    print(f"Data range: {start_date} to {end_date}")


    for location in weather_config["locations"]:
        name = location["name"]

        print(f"  Fetching {name}...")

        result = client.fetch_location(
            name=name,
            latitude=location["latitude"],
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )

        results.append(result)

        hourly = result["data"].get("hourly", {})
        timestamps = hourly.get("time", [])

        print(
            f"  {len(timestamps)} hourly records"
        )

    output_path = client.save_raw(
        results,
        "data/raw/open-meteo",
    )

    print(
        f"Raw weather data saved to: {output_path}"
    )

def main():
    config = load_config()

    ingest_world_bank(config)
    ingest_open_meteo(config)


if __name__ == "__main__":
    main()