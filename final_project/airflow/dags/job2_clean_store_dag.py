from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="job2_kafka_to_sqlite",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["kafka", "sqlite"]
) as dag:

    run_cleaner = BashOperator(
        task_id="run_cleaner_job",
        bash_command="python src/job2_cleaner.py || true"
    )

    run_cleaner
