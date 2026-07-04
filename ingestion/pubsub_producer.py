import json
import time
import random
import pandas as pd
from google.cloud import pubsub_v1
from pipeline.config import GCP_PROJECT_ID
import os

TOPIC = os.getenv("PUBSUB_TOPIC", "pos-live-feed")

def stream_events(delay=0.05, n_events=500):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, TOPIC)

    df = pd.read_csv("data/sample/pos_transactions.csv").sample(n_events)
    for _, row in df.iterrows():
        event = {
            "store_id": row.store_id,
            "sku_id": row.sku_id,
            "qty_sold": int(row.qty_sold),
            "stock_on_hand": int(row.stock_on_hand),
            "timestamp": time.time(),
        }
        publisher.publish(topic_path, json.dumps(event).encode("utf-8"))
        time.sleep(delay)
    print(f"Streamed {n_events} live events to {TOPIC}")

if __name__ == "__main__":
    stream_events()