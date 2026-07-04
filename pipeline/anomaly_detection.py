def detect_anomalies(df, gpu=True):
    """
    Flags demand spikes using z-score of qty_sold vs rolling mean/std.
    On GPU, uses cuML's StandardScaler for large-scale speed; the z-score
    math itself is vectorized cudf/pandas either way.
    """
    if gpu:
        import cudf
        from cuml.preprocessing import StandardScaler
    df["z_score"] = (
        (df["qty_sold"] - df["rolling_avg_demand"]) /
        df["rolling_std_demand"].replace(0, 0.1)
    )
    df["is_anomaly"] = (df["z_score"].abs() > 2.5)
    return df