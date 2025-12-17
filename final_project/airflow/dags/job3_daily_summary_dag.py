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
        bash_command="/Users/hwanganna/final_project/.venv_airflow/bin/python /Users/hwanganna/final_project/src/job3_analytics.py"
    )

    run_analytics
