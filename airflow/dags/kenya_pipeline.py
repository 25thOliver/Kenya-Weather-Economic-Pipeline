from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


@dag(
    dag_id="kenya_economic_weather_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["kenya", "data-engineering"],
)
def kenya_economic_weather_pipeline():

    @task(
        retries=3,
        retry_delay=timedelta(minutes=5),
        retry_exponential_backoff=True,
    )
    def run_economic():
        from pathlib import Path
        import yaml
        from storage import MinioStorage
        from pipelines.economic_pipeline import run_economic_pipeline

        with Path("/app/config/sources.yml").open(
            "r", encoding="utf-8"
        ) as file:
            config = yaml.safe_load(file)

        storage = MinioStorage()
        storage.ensure_bucket()

        return run_economic_pipeline(config, storage)

    @task(
        retries=3,
        retry_delay=timedelta(minutes=5),
        retry_exponential_backoff=True,
    )
    def run_weather():
        from pathlib import Path
        import yaml
        from storage import MinioStorage
        from pipelines.weather_pipeline import run_weather_pipeline
        from watermarks import WatermarkManager

        with Path("/app/config/sources.yml").open(
            "r", encoding="utf-8"
        ) as file:
            config = yaml.safe_load(file)

        storage = MinioStorage()
        storage.ensure_bucket()

        watermark = WatermarkManager()
        try:
            result = run_weather_pipeline(
                config,
                storage,
                watermark_manager=watermark,
            )
        finally:
            watermark.close()

        return result 

    @task(
        retries=2,
        retry_delay=timedelta(minutes=2),
    )
    def load_database(economic_result, weather_result):
        from pipelines.database_pipeline import load_processed_data

        return load_processed_data(
            weather_result=weather_result,
        )

    economic = run_economic()
    weather = run_weather()

    # Pass weather result directly into load_database via XCom
    database = load_database(economic, weather)

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command="""
            cd /app/dbt
            dbt docs generate \
                --log-path /tmp/dbt-logs \
                --target-path /tmp/dbt-target
        """,
    )


    database >> dbt_build >> dbt_docs


kenya_economic_weather_pipeline()
