import json
import os
from pathlib import Path

import psycopg2

class PostgresLoader:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"]
        )

    def load_economic_indicators(
            self,
            input_path: str,
            
    ) -> int:

        input_file = Path(input_path)

        with input_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            records = json.load(file)

        inserted = 0

        with self.connection.cursor() as cursor:

            for record in records:

                cursor.execute(
                    """
                    INSERT INTO economic_indicators (
                        country_code,
                        country,
                        indicator_code,
                        year,
                        value
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (
                        country_code,
                        indicator_code,
                        year
                    )
                    DO UPDATE SET
                        value = EXCLUDED.value,
                        country = EXCLUDED.country
                    """,

                    (
                        record["country_code"],
                        record["country"],
                        record["indicator_code"],
                        record["year"],
                        record["value"],
                    ),
                )

                inserted += cursor.rowcount

        self.connection.commit()

        return inserted

    def load_daily_weather(
            self,
            input_path: str,
    )  -> int:

        input_file = Path(input_path)

        with input_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            records = json.load(file)

        inserted = 0

        with self.connection.cursor() as cursor:

            for record in records:

                cursor.execute(
                    """
                    INSERT INTO daily_weather (
                        date,
                        location,
                        temperature_avg,
                        temperature_min,
                        temperature_max,
                        rainfall,
                        humidity_avg,
                        wind_speed_avg
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    ON CONFLICT (
                        date,
                        location
                    )
                    DO NOTHING
                    """,
                    (
                        record["date"],
                        record["location"],
                        record["temperature_avg"],
                        record["temperature_min"],
                        record["temperature_max"],
                        record["rainfall"],
                        record["humidity_avg"],
                        record["wind_speed_avg"],
                    ),
                    
                )

                inserted += cursor.rowcount

        self.connection.commit()

        return inserted

    def close(self):
        self.connection.close()