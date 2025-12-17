import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

SQLITE_PATH = os.getenv("SQLITE_PATH", "./data/app.db")



def init_summary_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            total_articles INTEGER,
            unique_sources INTEGER,
            avg_title_length REAL
        )
    """)
    conn.commit()


def table_exists(conn, table_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None


#analytics
def compute_global_summary(conn):
    if not table_exists(conn, "events"):
        print("Table events does not exist. Skipping analytics.")
        return None

    df = pd.read_sql("SELECT * FROM events", conn)

    if df.empty:
        print("Events table is empty. Skipping analytics.")
        return None

    summary = pd.DataFrame([{
        "total_articles": len(df),
        "unique_sources": df["source_name"].nunique(),
        "avg_title_length": round(df["title"].astype(str).str.len().mean(), 2)
    }])

    return summary



def write_summary(conn, df: pd.DataFrame):
    df.to_sql("daily_summary", conn, if_exists="append", index=False)


def main():
    print("Job 3 started: Global analytics")

    if not os.path.exists(SQLITE_PATH):
        print("Database file does not exist. Exiting.")
        return

    conn = sqlite3.connect(SQLITE_PATH)

    init_summary_table(conn)

    summary_df = compute_global_summary(conn)

    if summary_df is None:
        print("No analytics written")
        conn.close()
        return

    write_summary(conn, summary_df)
    conn.close()

    print("Daily summary written successfully")
    print(summary_df)


if __name__ == "__main__":
    main()
