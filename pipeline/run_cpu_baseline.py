import pandas as pd
import time
from pipeline.config import POS_CLEAN_PATH
from pipeline.features import add_demand_features
from pipeline.anomaly_detection import detect_anomalies
from pipeline.risk_fusion import fuse_risk_signals

def run():
    t0 = time.time()
    df = pd.read_parquet(POS_CLEAN_PATH)
    df = add_demand_features(df)
    df = detect_anomalies(df, gpu=False)
    df = fuse_risk_signals(df)
    total = time.time() - t0
    print(f"CPU pandas total time: {total:.2f}s")
    return total

if __name__ == "__main__":
    run()