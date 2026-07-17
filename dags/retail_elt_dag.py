"""
Retail ELT pipeline DAG.

    generate_or_check_data  ->  load_raw_to_snowflake  ->  dbt_run  ->  dbt_test

Scheduled daily. In an interview, the story is:
ingestion is idempotent (CREATE OR REPLACE + COPY INTO), transforms are
versioned SQL in dbt, and quality gates (dbt test) block bad data from
reaching the marts.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/elt-pipeline"          # adjust to your mount
DBT_DIR = f"{PROJECT_DIR}/dbt/retail_analytics"

default_args = {
    "owner": "haytem",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="retail_elt_pipeline",
    description="Load raw retail data to Snowflake, transform with dbt, run quality tests",
    schedule="@daily",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    default_args=default_args,
    tags=["elt", "snowflake", "dbt"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_or_check_data",
        bash_command=f"cd {PROJECT_DIR}/ingestion && python generate_data.py",
    )

    load_raw = BashOperator(
        task_id="load_raw_to_snowflake",
        bash_command=f"cd {PROJECT_DIR}/ingestion && python load_to_snowflake.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir /home/airflow/.dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir /home/airflow/.dbt",
    )

    generate_data >> load_raw >> dbt_run >> dbt_test
