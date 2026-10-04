FROM apache/airflow:2.10.5-python3.12

USER airflow

RUN pip install --no-cache-dir \
    pyyaml \
    boto3 \
    psycopg2-binary \
    requests \
    dbt-core==1.11.15 \
    dbt-postgres==1.11.0