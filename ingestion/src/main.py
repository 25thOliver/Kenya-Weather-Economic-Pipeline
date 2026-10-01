from pathlib import Path
import yaml
from storage import MinioStorage
from pipelines.economic_pipeline import (
    run_economic_pipeline,
)

from pipelines.weather_pipeline import (
    run_weather_pipeline,
)

from pipelines.database_pipeline import (
    load_processed_data,
)

def load_config():
    config_path = Path("config/sources.yml")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    config = load_config()

    storage = MinioStorage()
    storage.ensure_bucket()

    run_economic_pipeline(
        config,
        storage,
        )

    
    run_weather_pipeline(
        config,
        storage,
        )

    load_processed_data()

if __name__ == "__main__":
    main()