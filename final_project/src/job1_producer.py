import os
import json
import time
from datetime import datetime, timezone

import requests
from kafka import KafkaProducer
from dotenv import load_dotenv



load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC_RAW", "raw_gnews_events")


QUERY = "technology"


FETCH_INTERVAL_SECONDS = 60

GNEWS_URL = "https://gnews.io/api/v4/search"


#kafka
def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
    )



def fetch_articles(from_iso: str | None = None) -> list[dict]:
    params = {
        "q": QUERY,
        "token": GNEWS_API_KEY,
        "lang": "en",
        "max": 10,
        "sortby": "publishedAt"
    }

    if from_iso:
        params["from"] = from_iso

    response = requests.get(GNEWS_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data.get("articles", [])



def main():
    if not GNEWS_API_KEY:
        raise RuntimeError("GNEWS_API_KEY not found in .env")

    producer = create_producer()
    last_fetch_time = None

    print("GNews Kafka producer started")
    print(f"Topic: {TOPIC}")
    print(f"Query: {QUERY}")
    print("Press Ctrl+C to stop")

    while True:
        try:
            articles = fetch_articles(last_fetch_time)

            sent_count = 0
            fetch_time_utc = datetime.now(timezone.utc).isoformat()

            for article in articles:
                article_id = article.get("id")
                published_at = article.get("publishedAt")

                if not article_id or not published_at:
                    continue

                msg = {
                    "article_id": article_id,
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "content": article.get("content"),
                    "url": article.get("url"),
                    "image": article.get("image"),
                    "published_at": published_at,
                    "source_name": article.get("source", {}).get("name"),
                    "query": QUERY,
                    "fetched_at_utc": fetch_time_utc
                }

                producer.send(TOPIC, value=msg)
                sent_count += 1

            producer.flush()

            if articles:
                
                last_fetch_time = max(
                    a["publishedAt"] for a in articles if "publishedAt" in a
                )

            print(
                f"[{fetch_time_utc}] fetched={len(articles)} sent={sent_count}"
            )

        except Exception as e:
            print("ERROR:", e)

        time.sleep(FETCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
