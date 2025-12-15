from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="job3_daily_analytics",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["analytics", "sqlite"]
) as dag:

    run_analytics = BashOperator(
        task_id="run_daily_analytics",
        bash_command="python src/job3_analytics.py || true"
    )

    run_analytics
