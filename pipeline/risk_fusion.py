def fuse_risk_signals(df):
    """
    Final risk score = weighted combination of:
      - stockout urgency (low days_of_stock_left)
      - demand anomaly (spike detected)
      - velocity change (trending up = more urgent)
    """
    df["stockout_urgency"] = (1 / (df["days_of_stock_left"] + 1)).clip(0, 1)
    df["anomaly_boost"] = df["is_anomaly"].astype(int) * 0.2
    df["velocity_boost"] = (df["velocity_change"].clip(lower=0) * 0.1).clip(upper=0.2)

    df["stockout_risk"] = (
        df["stockout_urgency"] * 0.7 + df["anomaly_boost"] + df["velocity_boost"]
    ).clip(0, 1)

    df["risk_tier"] = df["stockout_risk"].apply(
        lambda x: "CRITICAL" if x > 0.75 else ("WARNING" if x > 0.5 else "OK")
    )
    return df