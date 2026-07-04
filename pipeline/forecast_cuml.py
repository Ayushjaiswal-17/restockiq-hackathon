def forecast_top_risk_skus(gdf, top_risk_pairs, gpu=True):
    """
    Runs a lightweight per-(store,sku) linear forecast only for the
    highest-risk combos (keeps it demo-fast: ~200 models, not 100K).
    """
    if gpu:
        import cudf
        from cuml.linear_model import LinearRegression
    else:
        import pandas as cudf
        from sklearn.linear_model import LinearRegression

    results = []
    gdf["day_num"] = cudf.to_datetime(gdf["date"]).astype("int64") // 86_400_000_000_000

    for store, sku in top_risk_pairs:
        sub = gdf[(gdf.store_id == store) & (gdf.sku_id == sku)]
        if len(sub) < 10:
            continue
        X = sub[["day_num"]]
        y = sub["qty_sold"]
        model = LinearRegression()
        model.fit(X, y)
        next_day = X["day_num"].max() + 1
        pred = model.predict(cudf.DataFrame({"day_num": [next_day]}))
        results.append((store, sku, float(pred.iloc[0])))

    cols = ["store_id", "sku_id", "forecast_qty"]
    return cudf.DataFrame(results, columns=cols) if gpu else __import__("pandas").DataFrame(results, columns=cols)