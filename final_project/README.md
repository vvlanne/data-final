# Final Project – Kafka + Python Scripts + Airflow

**GNews API:** [https://gnews.io](https://gnews.io)  
**Students:** Ilyassova Kamilla, Khvan Anna, Kelis Karina

---

This project fetches news data via GNews API, sends it to Kafka, processes it with Python scripts, stores it in SQLite, and runs analytics via Airflow DAGs.

---

## **How to Run**

### **0) Open VS Code Terminal**
```bash
cd ~/final_project
pwd
# Expected: path ends with final_project
Part A – Kafka
Start Docker Desktop and wait until it runs.

Check Docker daemon:

bash
Копировать код
docker info
Start Kafka containers:

bash
Копировать код
cd ~/kafka-local
docker-compose up -d
docker ps
Optional: check logs

bash
Копировать код
docker logs --tail 50 kafka-local-kafka-1
Part B – Python Environment
Create virtual environment and activate:

bash
Копировать код
cd ~/final_project
python3 -m venv .venv
source .venv/bin/activate
Install dependencies:

bash
Копировать код
pip install --upgrade pip
pip install -r requirements.txt
Quick sanity check:

bash
Копировать код
python -c "import pandas, kafka; print('OK')"
# Expected: OK
Part C – Run Scripts Manually
Job 1 – Producer (fetches data from GNews → Kafka)

bash
Копировать код
python src/job1_producer.py
# Let it run 30-60 sec, then Ctrl+C
Job 2 – Cleaner (Kafka → clean → SQLite)

bash
Копировать код
python src/job2_cleaner.py
Check SQLite tables

bash
Копировать код
sqlite3 data/app.db
.tables
.quit
Job 3 – Analytics (process daily summary)

bash
Копировать код
python src/job3_analytics.py
Part D – Airflow
Create separate Airflow venv:

bash
Копировать код
python3 -m venv .venv_airflow
source .venv_airflow/bin/activate
pip install --upgrade pip
pip install apache-airflow==2.8.1
pip install -r requirements.txt
Initialize Airflow:

bash
Копировать код
export AIRFLOW_HOME=~/final_project/airflow
mkdir -p $AIRFLOW_HOME
airflow db init
Create admin user:

bash
Копировать код
airflow users create \
  --username admin \
  --firstname admin \
  --lastname admin \
  --role Admin \
  --email admin@example.com
DAGs folder:

bash
Копировать код
export AIRFLOW__CORE__DAGS_FOLDER=~/final_project/airflow/dags
airflow dags list
Start Airflow webserver + scheduler:
Terminal 1

bash
Копировать код
airflow webserver -p 8080
Terminal 2

bash
Копировать код
airflow scheduler
Open UI: http://localhost:8080 (login: admin + password)

Part E – Run DAGs
Run Job 1 manually 30-60 sec first (avoid Airflow killing it).

Trigger DAGs in order:

job2_kafka_to_sqlite → wait SUCCESS

job3_daily_analytics → wait SUCCESS

Job 1 DAG can run, but may be terminated if too long.

