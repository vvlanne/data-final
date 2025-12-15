import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv



load_dotenv()

SQLITE_PATH = os.getenv("SQLITE_PATH", "./data/app.db")



def init_summary_table():
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_articles INTEGER,
            unique_sources INTEGER,
            top_source TEXT,
            top_source_count INTEGER,
            avg_title_length REAL
        )
    """)

    conn.commit()
    conn.close()


#analytics
def compute_summary():
    conn = sqlite3.connect(SQLITE_PATH)

    query = """
        SELECT *
        FROM events
    """

    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("No data found in events table")
        return None

    total_articles = len(df)
    unique_sources = df["source_name"].nunique()

    source_counts = df["source_name"].value_counts()
    top_source = source_counts.idxmax()
    top_source_count = int(source_counts.max())

    avg_title_length = round(
        df["title"].astype(str).str.len().mean(), 2
    )

    summary = pd.DataFrame([{
        "total_articles": total_articles,
        "unique_sources": unique_sources,
        "top_source": top_source,
        "top_source_count": top_source_count,
        "avg_title_length": avg_title_length
    }])

    return summary


# ================= WRITE =================
def write_summary(df: pd.DataFrame):
    conn = sqlite3.connect(SQLITE_PATH)
    df.to_sql("daily_summary", conn, if_exists="append", index=False)
    conn.close()


# ================= MAIN =================
def main():
    print("Job 3 started: Global analytics")

    init_summary_table()

    summary_df = compute_summary()

    if summary_df is None:
        print("No summary written")
        return

    write_summary(summary_df)
    print("Global summary written successfully")
    print(summary_df)


if __name__ == "__main__":
    main()
