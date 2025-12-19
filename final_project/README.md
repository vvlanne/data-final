# Final Project – Kafka + Python Scripts + Airflow

**GNews API:** [https://gnews.io](https://gnews.io)  
**Students:** Ilyassova Kamilla, Khvan Anna, Kelis Karina

---

This project fetches news data via GNews API, sends it to Kafka, processes it with Python scripts, stores it in SQLite, and runs analytics via Airflow DAGs.

---

## **How to Run (for MacOS)**

### **Part A - Kafka**
1) Start Docker Desktop and wait until it runs.

   Check Docker daemon:
```bash
docker info
```

2) Start Kafka containers:
```bash
cd ~/kafka-local
docker-compose up -d
docker ps
```

### **Part B - Python Environment**
3) Create virtual environment and activate:
```bash
cd ~/final_project
python3 -m venv .venv
source .venv/bin/activate
```

4) Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Part C – Run Scripts Manually**
Job 1 – Producer (fetches data from GNews → Kafka)
```bash
python src/job1_producer.py
```

Job 2 – Cleaner (Kafka → clean → SQLite)
```bash
python src/job2_cleaner.py
```

Job 3 – Analytics (process daily summary)
```bash
python src/job3_analytics.py
```

### **Part D – Airflow**
Create separate Airflow venv:
```bash
cd ~/final_project
python3 -m venv .venv_airflow
source .venv_airflow/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Initialize Airflow:
```bash
export AIRFLOW_HOME=~/final_project/airflow
mkdir -p $AIRFLOW_HOME
airflow db init
```

Create admin user:
```bash
airflow users create \
  --username admin \
  --firstname admin \
  --lastname admin \
  --role Admin \
  --email admin@example.com
```

Start Airflow webserver + scheduler:

Terminal 1
```bash
source .venv_airflow/bin/activate
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW_HOME=~/final_project/airflow
export AIRFLOW__CORE__DAGS_FOLDER=~/final_project/airflow/dags
airflow webserver -p 8080
```

Terminal 2
```bash
source .venv_airflow/bin/activate
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW_HOME=~/final_project/airflow
export AIRFLOW__CORE__DAGS_FOLDER=~/final_project/airflow/dags
airflow scheduler
```

Open UI: http://localhost:8080 

### **Part E – Run DAGs**
Trigger the DAGs in the following order:


Start Job 1 and allow it to complete successfully.

After Job 1 has finished, stop it.

Then trigger Job 2, followed by Job 3, ensuring they run sequentially.









