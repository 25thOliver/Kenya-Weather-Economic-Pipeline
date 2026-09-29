from collections import defaultdict
from pathlib import Path
import json


def transform_weather(
        inputh_path: str,
        output_path: str,
):
    input_file = Path(inputh_path)
    output_file = Path(output_path)


    with input_file.open("r", encoding="utf-8") as file:
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
        temperatures = hourly.get("temperature_2m", [])
        rainfall = hourly.get("precipitation", [])
        humidity = hourly.get(
            "relative_humidity_2m", []
        )
        wind_speed = hourly.get(
            "wind_speed_10m", []
        )

        for index, timestamp in enumerate(times):
            date = timestamp[:10]

            key = (date, location)

            if index < len(temperatures):
                value = temperatures[index]
                if value is not None:
                    daily[key]["temperatures"].append(
                        value
                    )

            if index < len(rainfall):
                value = rainfall[index]
                if value is not None:
                    daily[key]["rainfall"].append(
                        value
                    )

            if index < len(humidity):
                value = humidity[index]
                if value is not None:
                    daily[key]["humidity"].append(
                        value
                    )

            if index < len(humidity):
                value = wind_speed[index]
                if value is not None:
                    daily[key]["wind_speed"].append(
                        value
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
                    "temperature_avg": (
                        sum(temperatures)
                        / len(temperatures)
                        if temperatures
                        else None
                    ),
                    "temperature_min": (
                        min(temperatures)
                        if temperatures
                        else None
                    ),
                    "temperature_max": (
                        max(temperatures)
                        if temperatures
                        else None
                    ),
                    "rainfall": sum(rainfall),
                    "humidity_avg": (
                        sum(humidity)
                        / len(humidity)
                        if humidity
                        else None
                    ),
                    "wind_speed_avg": (
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