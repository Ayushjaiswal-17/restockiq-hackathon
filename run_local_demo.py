import os
import pprint

from data.generate_data import generate as generate_data
from data.generate_copurchase_graph import generate as generate_graph
from pipeline.run_local_pipeline import run_local_pipeline


def simple_po_from_row(row):
    forecast = row.get("forecast_qty", 0) if "forecast_qty" in row.index else 0
    recommended_qty = int(max(1, round(float(forecast) * 14))) if forecast and not pd_isna(forecast) else 10
    return {
        "sku_id": row.sku_id,
        "store_id": row.store_id,
        "recommended_qty": recommended_qty,
        "urgency": "HIGH",
        "justification": f"Risk {row.stockout_risk:.2f}, days left {row.days_of_stock_left:.1f}",
    }


def pd_isna(x):
    try:
        import pandas as _pd

        return _pd.isna(x)
    except Exception:
        return x is None


def main():
    os.makedirs("data/sample", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    print("1) Generating sample data (this may take a moment)...")
    generate_data()
    generate_graph()

    print("2) Running local CPU pipeline...")
    final = run_local_pipeline()

    print("Top 10 risk items:")
    print(final.sort_values("stockout_risk", ascending=False).head(10).to_string(index=False))

    # Draft simple purchase orders for critical items
    critical = final[final.risk_tier == "CRITICAL"]
    print(f"Drafting POs for {len(critical):,} critical items (auto-approve threshold 50)")

    # simple approval logic from agent.po_approval
    from agent.po_approval import approve_po

    pos = []
    for _, row in critical.iterrows():
        po = simple_po_from_row(row)
        po = approve_po(po)
        pos.append(po)

    print("Sample approved POs (up to 10):")
    pprint.pprint(pos[:10])


if __name__ == "__main__":
    main()
