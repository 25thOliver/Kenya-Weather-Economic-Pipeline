import sys
from datetime import datetime
from airflow.decorators import dag, task


sys.path.insert(
    0,
    "opt/airflow/ingestion/src",
)

@dag(
    dag_id="kenya_economic_weather_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["kenya", "data-engineering"],
)

def kenya_eceonomic_weather_pipeline():

    @task
    def run_economic():
        from pathlib import Path
        import yaml
        from storage import MinioStorage
        from pipelines.economic_pipeline import (
            run_economic_pipeline,
        )

        with Path(
            "/opt/airflow/config/sources.yml"
        ).open(
            "r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file)


        storage = MinioStorage()
        storage.ensure_bucket()

        return run_economic_pipeline(
            config,
            storage,
        )

    @task
    def run_weather():
        from pathlib import Path
        import yaml

        from storage import MinioStorage
        from pipelines.weather_pipeline import (
            run_weather_pipeline,
        )

        with Path(
            "/opt/airflow/config/sources.yml"
        ).open(
            "r",
            encoding="utf-8"
        ) as file:
            config = yaml.safe_load(file)


        storage = MinioStorage()
        storage.ensure_bucket()

        return run_weather_pipeline(
            config,
            storage,
        )

    @task
    def laod_database():
        from pipelines.database_pipeline import (
            load_processed_data,
        )

        return load_processed_data()

    economic = run_economic()
    weather = run_weather()

    [economic, weather] >> laod_database()

kenya_eceonomic_weather_pipeline()