# Kenya Economic & Weather Intelligence Pipeline

A production-grade, fully Dockerized data engineering pipeline that ingests, stores, transforms, and visualizes economic and weather data for Kenya.

Built as a portfolio project demonstrating real-world data engineering practices: incremental ingestion, idempotent upserts, a dbt mart layer, Airflow orchestration, and MinIO raw data preservation.

---

## What It Does

| Layer | What happens |
|---|---|
| **Extract** | Fetches World Bank economic indicators and Open-Meteo hourly weather via REST API |
| **Raw Storage** | Uploads timestamped JSON snapshots to MinIO (S3-compatible data lake) |
| **Transform** | Aggregates hourly weather to daily; flattens World Bank nested records |
| **Load** | Upserts processed records into PostgreSQL (idempotent, revision-safe) |
| **Model** | dbt builds staging views and analytical mart tables |
| **Orchestrate** | Airflow DAG runs daily; weather uses watermarks for incremental-only fetches |
| **Visualise** | Apache Superset dashboards query the mart layer |

---