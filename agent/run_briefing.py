"""
Generates a plain-English daily inventory briefing from local risk_scores.parquet
using the Gemini API. No BigQuery / GCP billing required.

Usage:
    python agent/run_briefing.py
"""
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

RISK_PATH = "data/sample/risk_scores.parquet"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise SystemExit(
        "GEMINI_API_KEY not found. Add it to your .env file "
        "(get one free at https://aistudio.google.com/apikey)"
    )

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

BRIEFING_PROMPT = """
You are an autonomous inventory operations agent. Given this stockout risk data
(store, sku, risk tier, risk score, days of stock left), write a concise daily
briefing for a store operations manager:

1. Open with a one-line summary of overall inventory health today.
2. List the top 5-10 highest-risk items, grouped by store if possible, with
   days of stock left.
3. End with ONE clear recommended action (e.g. "Prioritize emergency reorder
   for these N items today").

Keep it under 200 words, plain English, no markdown headers.

Data:
{data}
"""


def load_top_risk(n=15):
    df = pd.read_parquet(
        RISK_PATH,
        columns=["date", "store_id", "sku_id", "stockout_risk",
                 "risk_tier", "days_of_stock_left"]
    )
    latest = df.sort_values("date").groupby(["store_id", "sku_id"]).tail(1)
    return latest.sort_values("stockout_risk", ascending=False).head(n)


def generate_briefing(top_df):
    data_str = top_df[
        ["store_id", "sku_id", "risk_tier", "stockout_risk", "days_of_stock_left"]
    ].to_string(index=False)
    prompt = BRIEFING_PROMPT.format(data=data_str)
    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    if not os.path.exists(RISK_PATH):
        raise SystemExit(f"Could not find {RISK_PATH}. Run the pipeline first.")

    top = load_top_risk()
    print(f"Loaded top {len(top)} highest-risk SKU-store combos.\n")
    print("Generating briefing with Gemini...\n")

    briefing = generate_briefing(top)

    print("=" * 60)
    print("DAILY INVENTORY BRIEFING")
    print("=" * 60)
    print(briefing)

    # Save it so the dashboard can optionally display it too
    with open("data/sample/latest_briefing.txt", "w", encoding="utf-8") as f:
        f.write(briefing)
    print("\nSaved to data/sample/latest_briefing.txt")