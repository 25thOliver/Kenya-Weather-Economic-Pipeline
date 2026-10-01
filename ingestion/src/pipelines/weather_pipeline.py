from clients.open_meteo import OpenMeteoClient
from transformers.weather import transform_weather


def run_weather_pipeline(config, storage):
    weather_config = config["weather"]

    client = OpenMeteoClient(
        base_url=weather_config["base_url"],
        timezone_name=weather_config["timezone"],
    )

    variables = weather_config["variables"]

    start_date = "2025-01-01"
    end_date = "2025-01-07"


    results = []

    print()
    print("Starting Open-Meteo pipeline...")
    print(
        f"Locations: "
        f"{len(weather_config['locations'])}"
    )
    print(
        f"Variables: {len(variables)}"
    )
    print(
        f"Data range: "
        f"{start_date} to {end_date}"
    )

    for location in weather_config["locations"]:
        name = location["name"]

        print(f"  Fetching {name}...")

        result = client.fetch_location(
            name=name,
            latitude=location["latitude"],
            longitude=location["longitude"],
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )

        results.append(result)

        hourly = result["data"].get(
            "hourly",
            {},
        )

        timestamps = hourly.get(
            "time",
            [],
        )

        print(
            f"   {len(timestamps)} hourly records"
        )

    raw_path = client.save_raw(
        results,
        "data/raw/open-meteo",
    )

    print(
        f"Raw weather data saved to: "
        f"{raw_path}"
    )

    object_key = (
        f"open-meteo/{raw_path.name}"
    )

    storage_path = storage.upload_file(
        str(raw_path),
        object_key,
    )

    print(
        f"Uploaded to MinIO: {storage_path}"
    )

    processed_path = (
        "data/processed/weather/"
        "weather_daily.json"
    )

    transform_weather(
        str(raw_path),
        processed_path,
    )

    print(
        f"Processed data saved to: "
        f"{processed_path}"
    )

    return processed_path