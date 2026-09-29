from collections import defaultdict
from pathlib import Path
import json


def round_value(value, decimals=2):
    if value is None:
        return None

    return round(value, decimals)


def transform_weather(
    input_path: str,
    output_path: str,
):
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        locations = json.load(file)

    daily = defaultdict(
        lambda: {
            "temperatures": [],
            "rainfall": [],
            "humidity": [],
            "wind_speed": [],
        }
    )

    for location_data in locations:

        location = location_data["location"]["name"]

        hourly = location_data["data"]["hourly"]

        times = hourly["time"]
        temperatures = hourly["temperature_2m"]
        rainfall = hourly["precipitation"]
        humidity = hourly["relative_humidity_2m"]
        wind_speed = hourly["wind_speed_10m"]

        for index, timestamp in enumerate(times):

            date = timestamp[:10]

            key = (date, location)

            if temperatures[index] is not None:
                daily[key]["temperatures"].append(
                    temperatures[index]
                )

            if rainfall[index] is not None:
                daily[key]["rainfall"].append(
                    rainfall[index]
                )

            if humidity[index] is not None:
                daily[key]["humidity"].append(
                    humidity[index]
                )

            if wind_speed[index] is not None:
                daily[key]["wind_speed"].append(
                    wind_speed[index]
                )

    transformed = []

    for (date, location), values in sorted(
        daily.items()
    ):

        temperatures = values["temperatures"]
        rainfall = values["rainfall"]
        humidity = values["humidity"]
        wind_speed = values["wind_speed"]

        transformed.append(
            {
                "date": date,
                "location": location,
                "temperature_avg": round_value(
                    sum(temperatures)
                    / len(temperatures)
                    if temperatures
                    else None
                ),
                "temperature_min": round_value(
                    min(temperatures)
                    if temperatures
                    else None
                ),
                "temperature_max": round_value(
                    max(temperatures)
                    if temperatures
                    else None
                ),
                "rainfall": round_value(
                    sum(rainfall)
                ),
                "humidity_avg": round_value(
                    sum(humidity)
                    / len(humidity)
                    if humidity
                    else None
                ),
                "wind_speed_avg": round_value(
                    sum(wind_speed)
                    / len(wind_speed)
                    if wind_speed
                    else None
                ),
            }
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            transformed,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file