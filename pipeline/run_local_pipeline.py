import os
import pandas as pd

from pipeline.features import add_demand_features
from pipeline.anomaly_detection import detect_anomalies
from pipeline.risk_fusion import fuse_risk_signals


def run_local_pipeline(pos_csv="data/sample/pos_transactions.csv",
                       edges_csv="data/sample/copurchase_edges.csv",
                       out_csv="data/output/risk_scores.csv",
                       window_days=7,
                       top_n_subs=3):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    df = pd.read_csv(pos_csv, parse_dates=["date"]) if os.path.exists(pos_csv) else pd.DataFrame()
    if df.empty:
        raise FileNotFoundError(f"pos transactions CSV not found: {pos_csv}")

    df = add_demand_features(df, window_days=window_days)
    df = detect_anomalies(df, gpu=False)
    df = fuse_risk_signals(df)

    latest = df.sort_values("date").groupby(["store_id", "sku_id"]).tail(1)

    # Add a top substitute SKU where available
    if os.path.exists(edges_csv):
        edges_df = pd.read_csv(edges_csv)
        try:
            from pipeline.substitution_graph import get_top_substitutes

            def pick_sub(sku):
                subs = get_top_substitutes(None, sku, edges_df, top_n=top_n_subs)
                return subs[0] if subs else None

            latest["top_substitute"] = latest["sku_id"].apply(pick_sub)
        except Exception:
            latest["top_substitute"] = None
    else:
        latest["top_substitute"] = None

    latest.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with {len(latest):,} rows")
    return latest
