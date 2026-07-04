import google.generativeai as genai
from pipeline.config import GEMINI_API_KEY
from agent.prompts import DAILY_BRIEFING_PROMPT, PO_DRAFT_PROMPT
import json

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_daily_briefing(risk_df, top_n=15):
    top = risk_df.sort_values("stockout_risk", ascending=False).head(top_n)
    cols = ["store_id", "sku_id", "stockout_risk", "days_of_stock_left", "forecast_qty"]
    data_str = top[cols].to_string(index=False)
    prompt = DAILY_BRIEFING_PROMPT.format(data=data_str)
    response = model.generate_content(prompt)
    return response.text

def draft_purchase_order(row):
    prompt = PO_DRAFT_PROMPT.format(
        store_id=row.store_id, sku_id=row.sku_id,
        days_left=round(row.days_of_stock_left, 1),
        forecast_qty=round(row.get("forecast_qty", 0), 1)
    )
    response = model.generate_content(prompt)
    text = response.text.strip().strip("```json").strip("```")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": response.text}