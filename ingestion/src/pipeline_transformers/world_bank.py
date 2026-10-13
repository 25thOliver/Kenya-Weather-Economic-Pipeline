from pathlib import Path
import json

def transform_world_bank(
        input_path: str,
        output_path: str,
):

    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as file:
        data = json.load(file)


    transformed = []

    for record in data["records"]:
        transformed.append(
            {
                "country_code": record.get(
                    "countryiso3code"
                ),
                "country": (
                    record.get("country") or {}
                ).get("value"),
                "indicator_code": (
                    record.get("indicator") or {}
                ).get("id"),
                "year": int(record["date"]),
                "value": record.get("value"),
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
                       