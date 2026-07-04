DAILY_BRIEFING_PROMPT = """
You are an autonomous inventory operations agent. Given this stockout risk data
(store, sku, risk score, days of stock left, forecast demand, substitute SKUs),
write a concise daily briefing for a store manager:

1. List CRITICAL items first, with store, sku, and days left.
2. For each critical item, suggest the substitute SKU if one is available.
3. End with a one-line recommended action (e.g. "Approve emergency reorder for X items").

Data:
{data}
"""

PO_DRAFT_PROMPT = """
Based on this critical risk item, draft a short purchase order request:
Store: {store_id}, SKU: {sku_id}, Days of stock left: {days_left},
Forecast demand next period: {forecast_qty}.

Return JSON with fields: sku_id, store_id, recommended_qty, urgency, justification.
Recommend a quantity that covers 14 days of forecasted demand.
"""