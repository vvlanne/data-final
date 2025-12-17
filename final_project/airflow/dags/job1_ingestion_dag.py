from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="job1_gnews_ingestion",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["kafka", "api"]
) as dag:

    run_job1 = BashOperator(
        task_id="run_gnews_ingestion",
        bash_command="/Users/hwanganna/final_project/.venv/bin/python /Users/hwanganna/final_project/src/job1_producer.py"
    )
