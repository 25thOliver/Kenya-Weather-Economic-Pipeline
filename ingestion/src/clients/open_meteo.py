from pathlib import Path
from datetime import datetime, timezone
import json

import requests


class OpenMeteoClient:
    def __init__(self, base_url: str, timezone_name: str):
        self.base_url = base_url.rstrip("/")
        self.timezone_name = timezone_name


    def fetch_location(
            self,
            name: str,
            latitude: float,
            longitude: float,
            variables: list[str],
            start_date: str,
            end_date: str,
    )  -> dict:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(variables),
            "timezone": self.timezone_name,
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=30,

        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError(
                f"Unexpected Open-Meteo response for {name}"
            )
        if "error" in payload and payload["error"]:
            reason = payload.get(
                "reason",
                "Unknown Open-Meteo API error",
            )

            raise ValueError(
                f"Open-Meteo error for {name}: {reason}"
            )

        return {
            "location": {
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
            },
            "request": {
                "url": response.url,
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
            "data": payload,
        }

    @staticmethod
    def save_raw(
        data: list[dict],
        output_directory: str,
    ) -> Path:

        output_path = Path(output_directory)
        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")

        file_path = (
            output_path
            / f"opene_meteo_{timestamp}.json"
        )

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data, 
                file, 
                indent=2,
                ensure_ascii=False,
            )

        return file_path