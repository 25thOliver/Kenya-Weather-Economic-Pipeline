from pathlib import Path
from datetime import datetime, timezone

import requests


class WorldBankClient:
    def __init__(self, base_url: str, country_code: str):
        self.base_url = base_url.rstrip("/")
        self.country_code = country_code

    def fetch_indicators(self, indicator_codes: list[str]) -> dict:
        indicators = ";".join(indicator_codes)

        url = (
            f"{self.base_url}/country/"
            f"{self.country_code}/indicator/"
            f"{indicators}"
        )

        params = {
            "format": "json",
            "per_page": 1000,
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, list) or len(payload) != 2:
            raise ValueError(
                "Unexpected World Bank API response structure"
            )

        metadata = payload[0]
        records = payload[1]

        return {
            "metadata": metadata,
            "records": records,
            "request": {
                "url": response.url,
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        }

    @staticmethod
    def save_raw(data: dict, output_directory: str) -> Path:
        import json

        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        file_path = output_path / f"world_bank_{timestamp}.json"

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )
        return file_path