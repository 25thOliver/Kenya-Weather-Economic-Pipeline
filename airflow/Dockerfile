FROM apache/airflow:2.10.5-python3.12

USER airflow

RUN pip install --no-cache-dir \
    pyyaml \
    boto3 \
    psycopg2-binary \
    requests \
    tenacity==9.0.0 \
    dbt-core==1.9.3 \
    dbt-postgres==1.9.1
