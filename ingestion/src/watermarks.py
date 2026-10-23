"""
WatermarkManager — reads and writes pipeline run bookmarks.

Each pipeline stores its last successfully loaded date in the
pipeline_watermarks table. On the next run, it reads this date
and fetches only new data from that point forward.
"""
import logging
import os
from datetime import date, datetime, timezone

import psycopg2

logger = logging.getLogger(__name__)


class WatermarkManager:
    """
    Tracks the last successfully loaded date per pipeline.
    Uses the pipeline_watermarks PostgreSQL table as its store.
    """

    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

    def get_last_date(
        self,
        pipeline_name: str,
        default: date,
    ) -> date:
        """
        Return the last successfully loaded date for a pipeline.
        If no watermark exists (first ever run), return `default`.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT last_successful_date
                FROM pipeline_watermarks
                WHERE pipeline_name = %s
                """,
                (pipeline_name,),
            )
            row = cursor.fetchone()

        if row is None:
            logger.info(
                "No watermark for '%s'. Using default start: %s",
                pipeline_name,
                default,
            )
            return default

        logger.info(
            "Watermark for '%s': %s",
            pipeline_name,
            row[0],
        )
        return row[0]

    def set_last_date(
        self,
        pipeline_name: str,
        loaded_date: date,
        records_loaded: int,
    ) -> None:
        """
        Upsert the watermark after a successful pipeline run.
        Uses ON CONFLICT so first run inserts, subsequent runs update.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pipeline_watermarks (
                    pipeline_name,
                    last_successful_date,
                    last_run_at,
                    records_loaded
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (pipeline_name)
                DO UPDATE SET
                    last_successful_date = EXCLUDED.last_successful_date,
                    last_run_at          = EXCLUDED.last_run_at,
                    records_loaded       = EXCLUDED.records_loaded
                """,
                (
                    pipeline_name,
                    loaded_date,
                    datetime.now(timezone.utc),
                    records_loaded,
                ),
            )
        self.connection.commit()

        logger.info(
            "Watermark updated for '%s': %s (%d records loaded)",
            pipeline_name,
            loaded_date,
            records_loaded,
        )

    def close(self) -> None:
        self.connection.close()
