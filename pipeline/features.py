def add_demand_features(df, window_days=7):
    df = df.sort_values(["store_id", "sku_id", "date"])

    grouped = df.groupby(["store_id", "sku_id"])["qty_sold"]

    df["rolling_avg_demand"] = grouped.rolling(window_days, min_periods=1).mean().reset_index(level=[0,1], drop=True)
    df["rolling_std_demand"] = grouped.rolling(window_days, min_periods=1).std().reset_index(level=[0,1], drop=True).fillna(0)

    df["days_of_stock_left"] = df["stock_on_hand"] / df["rolling_avg_demand"].replace(0, 0.1)
    df["velocity_change"] = df.groupby(["store_id", "sku_id"])["qty_sold"].pct_change().fillna(0)
    return df