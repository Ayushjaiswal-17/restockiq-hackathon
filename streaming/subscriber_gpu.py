import cudf.pandas
cudf.pandas.install()

import json
import pandas as pd
from google.cloud import pubsub_v1
from pipeline.config import GCP_PROJECT_ID
import os

SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION", "pos-live-feed-sub")
BATCH = []
BATCH_SIZE = 100

def callback(message):
    global BATCH
    event = json.loads(message.data)
    BATCH.append(event)
    message.ack()

    if len(BATCH) >= BATCH_SIZE:
        df = pd.DataFrame(BATCH)
        # run lightweight risk scoring on the micro-batch (GPU-accelerated)
        df["days_of_stock_left"] = df["stock_on_hand"] / df["qty_sold"].replace(0, 0.1)
        df["stockout_risk"] = (1 / (df["days_of_stock_left"] + 1)).clip(0, 1)
        critical = df[df.stockout_risk > 0.75]
        if len(critical) > 0:
            print(f"[ALERT] {len(critical)} SKUs just crossed critical risk threshold")
        BATCH = []

def listen():
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(GCP_PROJECT_ID, SUBSCRIPTION)
    subscriber.subscribe(sub_path, callback=callback)
    print("Listening for live POS events...")
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    listen()