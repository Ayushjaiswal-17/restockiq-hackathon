import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

N_STORES = 50
N_SKUS = 2000
N_DAYS = 730
DAILY_SAMPLE = 40000  # transactions/day -> ~2.9M rows total


def generate(out_dir="data/sample"):
    os.makedirs(out_dir, exist_ok=True)
    stores = [f"store_{i}" for i in range(N_STORES)]
    skus = [f"sku_{i}" for i in range(N_SKUS)]
    start_date = datetime(2025, 1, 1)

    rows = []
    for day in range(N_DAYS):
        date = start_date + timedelta(days=day)
        idxs = np.random.choice(N_STORES * N_SKUS, size=DAILY_SAMPLE, replace=False)
        for idx in idxs:
            s = stores[idx % N_STORES]
            k = skus[(idx // N_STORES) % N_SKUS]
            base = np.random.poisson(5)
            seasonal = 1 + 0.3 * np.sin(day / 365 * 2 * np.pi)
            # inject occasional demand spikes (for anomaly detection to catch)
            spike = 5 if np.random.rand() < 0.002 else 1
            qty = max(0, int(base * seasonal * spike + np.random.randint(-2, 3)))
            rows.append([date, s, k, qty, np.random.randint(5, 100)])

    df = pd.DataFrame(rows, columns=["date", "store_id", "sku_id", "qty_sold", "stock_on_hand"])
    out_path = os.path.join(out_dir, "pos_transactions.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df):,} rows -> {out_path}")


if __name__ == "__main__":
    generate()