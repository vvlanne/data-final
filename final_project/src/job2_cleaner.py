import os
import json
import sqlite3

import pandas as pd
from kafka import KafkaConsumer
from dotenv import load_dotenv


# ================= CONFIG =================
load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC_RAW", "raw_gnews_events")
SQLITE_PATH = os.getenv("SQLITE_PATH", "./data/app.db")

CONSUMER_GROUP = "gnews_cleaner_group"


# ================= SQLITE =================
def init_db():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            article_id TEXT PRIMARY KEY,
            published_at TEXT,
            fetched_at_utc TEXT,
            source_name TEXT,
            title TEXT,
            description TEXT,
            url TEXT,
            query TEXT
        )
    """)

    conn.commit()
    conn.close()


# ================= KAFKA =================
def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=CONSUMER_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )


# ================= CLEANING =================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.dropna(subset=["article_id", "published_at", "url"])

    df["published_at"] = pd.to_datetime(
        df["published_at"], errors="coerce", utc=True
    )
    df["fetched_at_utc"] = pd.to_datetime(
        df["fetched_at_utc"], errors="coerce", utc=True
    )

    df = df.dropna(subset=["published_at"])

    df["source_name"] = (
        df["source_name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["title"] = df["title"].astype(str).str.strip()

    # убираем дубликаты по article_id
    df = df.drop_duplicates(subset=["article_id"])

    return df[
        [
            "article_id",
            "published_at",
            "fetched_at_utc",
            "source_name",
            "title",
            "description",
            "url",
            "query",
        ]
    ]


# ================= WRITE =================
def write_to_sqlite(df: pd.DataFrame):
    conn = sqlite3.connect(SQLITE_PATH)

    df.to_sql(
        "events",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()


# ================= MAIN =================
def main():
    print("Job 2 started: Kafka -> Cleaning -> SQLite")

    init_db()
    consumer = create_consumer()

    records = consumer.poll(timeout_ms=5000, max_records=500)

    messages = []
    for _, batch in records.items():
        for msg in batch:
            messages.append(msg.value)

    if not messages:
        print("No new messages in Kafka. Exiting.")
        consumer.close()
        return

    df_raw = pd.DataFrame(messages)
    print(f"Read {len(df_raw)} messages from Kafka")

    df_clean = clean_dataframe(df_raw)
    print(f"Cleaned rows after deduplication: {len(df_clean)}")

    if df_clean.empty:
        print("No new rows to insert")
        consumer.commit()
        consumer.close()
        return

    write_to_sqlite(df_clean)
    consumer.commit()
    consumer.close()

    print(f"Inserted {len(df_clean)} rows into SQLite ({SQLITE_PATH})")


if __name__ == "__main__":
    main()
