"""
Unit tests for the pure transformation functions.
These test business logic in isolation — no API calls,
no database, no file system state assumed.
"""
import json
import tempfile
from pathlib import Path

from transformers.weather import transform_weather
from transformers.world_bank import transform_world_bank


# Helpers

def write_json(data: dict | list, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f)


def read_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# World Bank transformer

WORLD_BANK_RAW = {
    "records": [
        {
            "countryiso3code": "KEN",
            "country": {"value": "Kenya"},
            "indicator": {"id": "NY.GDP.MKTP.CD"},
            "date": "2022",
            "value": 110000000000.0,
        },
        {
            "countryiso3code": "KEN",
            "country": {"value": "Kenya"},
            "indicator": {"id": "NY.GDP.MKTP.CD"},
            "date": "2021",
            "value": None,  # missing value, should still appear
        },
    ]
}


def test_world_bank_extracts_fields():
    """Transformer should flatten nested API structure correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "raw.json"
        output_path = Path(tmpdir) / "clean.json"

        write_json(WORLD_BANK_RAW, input_path)
        transform_world_bank(str(input_path), str(output_path))

        result = read_json(output_path)

    assert len(result) == 2

    first = result[0]
    assert first["country_code"] == "KEN"
    assert first["country"] == "Kenya"
    assert first["indicator_code"] == "NY.GDP.MKTP.CD"
    assert first["year"] == 2022
    assert first["value"] == 110000000000.0


def test_world_bank_handles_null_value():
    """Records with null values should be included, not dropped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "raw.json"
        output_path = Path(tmpdir) / "clean.json"

        write_json(WORLD_BANK_RAW, input_path)
        transform_world_bank(str(input_path), str(output_path))

        result = read_json(output_path)

    null_record = next(r for r in result if r["year"] == 2021)
    assert null_record["value"] is None


# Weather transformer

def _make_weather_raw(location: str, temp_values: list, rain_values: list):
    """Build a minimal Open-Meteo shaped payload for one location."""
    times = [f"2025-01-01T{h:02d}:00" for h in range(len(temp_values))]
    humidity = [60.0] * len(temp_values)
    wind = [10.0] * len(temp_values)
    return {
        "location": {"name": location, "latitude": 0.0, "longitude": 0.0},
        "request": {"url": "https://example.com", "retrieved_at": "2025-01-02T00:00:00+00:00"},
        "data": {
            "hourly": {
                "time": times,
                "temperature_2m": temp_values,
                "precipitation": rain_values,
                "relative_humidity_2m": humidity,
                "wind_speed_10m": wind,
            }
        },
    }


def test_weather_aggregates_hourly_to_daily():
    """24 hourly records for one day should produce 1 daily record."""
    temps = [20.0 + i * 0.1 for i in range(24)]  # 20.0 to 22.3
    rain = [0.1] * 24  # 0.1 mm per hour = 2.4 mm total

    raw = [_make_weather_raw("Nairobi", temps, rain)]

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "raw.json"
        output_path = Path(tmpdir) / "daily.json"

        write_json(raw, input_path)
        transform_weather(str(input_path), str(output_path))

        result = read_json(output_path)

    assert len(result) == 1
    row = result[0]

    assert row["date"] == "2025-01-01"
    assert row["location"] == "Nairobi"
    assert row["temperature_min"] == round(min(temps), 2)
    assert row["temperature_max"] == round(max(temps), 2)
    assert row["rainfall"] == round(sum(rain), 2)


def test_weather_handles_none_temperatures():
    """Hourly slots with None temperature should be skipped in the average."""
    temps = [None, None, 25.0, 27.0]
    rain = [0.0] * 4

    raw = [_make_weather_raw("Mombasa", temps, rain)]

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "raw.json"
        output_path = Path(tmpdir) / "daily.json"

        write_json(raw, input_path)
        transform_weather(str(input_path), str(output_path))

        result = read_json(output_path)

    assert len(result) == 1
    row = result[0]
    # Average of [25.0, 27.0] only = 26.0
    assert row["temperature_avg"] == 26.0


def test_weather_separates_locations():
    """Two locations on the same date should produce two rows."""
    temps = [22.0] * 4
    rain = [0.0] * 4

    raw = [
        _make_weather_raw("Nairobi", temps, rain),
        _make_weather_raw("Mombasa", temps, rain),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "raw.json"
        output_path = Path(tmpdir) / "daily.json"

        write_json(raw, input_path)
        transform_weather(str(input_path), str(output_path))

        result = read_json(output_path)

    assert len(result) == 2
    locations = {r["location"] for r in result}
    assert locations == {"Nairobi", "Mombasa"}
