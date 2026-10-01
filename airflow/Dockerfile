FROM apache/airflow:2.10.5-python3.12

USER root

RUN pip install --no-cache-dir \
    pyyaml \
    boto3 \
    psycopg2-binary \
    requests

USER airflow