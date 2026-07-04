import cudf.pandas
cudf.pandas.install()

import pandas as pd
import time
from pipeline.features import add_demand_features
from pipeline.anomaly_detection import detect_anomalies
from pipeline.risk_fusion import fuse_risk_signals

def run(pos_clean_path="pos_clean.parquet", output_path="risk_scores.parquet"):
    t0 = time.time()
    df = pd.read_parquet(pos_clean_path)
    df = add_demand_features(df)
    df = detect_anomalies(df, gpu=True)
    df = fuse_risk_signals(df)
    total = time.time() - t0
    print(f"GPU cudf.pandas total time: {total:.2f}s")
    df.to_parquet(output_path)
    return total

if __name__ == "__main__":
    run()