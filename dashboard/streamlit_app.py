import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------------------------
# CONFIG — local file paths (no BigQuery, no GCP billing required)
# ---------------------------------------------------------------------------
DATA_DIR = "data/sample"
RISK_PATH = os.path.join(DATA_DIR, "risk_scores.parquet")
if not os.path.exists(RISK_PATH):
    RISK_PATH = os.path.join(DATA_DIR, "risk_scores_demo.parquet")
BENCHMARK_PATH = os.path.join(DATA_DIR, "benchmark_log.csv")

st.set_page_config(page_title="RestockIQ Command Center", layout="wide")
st.title("🚨 RestockIQ — Autonomous Inventory Command Center")
st.caption("Running fully local (Parquet/CSV) — no BigQuery/GCP billing required.")

# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_risk():
    if not os.path.exists(RISK_PATH):
        return None

    # Only read the columns the dashboard actually needs — avoids loading
    # the full wide dataframe (and any heavy intermediate columns) into RAM.
    import pyarrow.parquet as pq
    available_cols = set(pq.ParquetFile(RISK_PATH).schema.names)

    wanted_cols = [c for c in [
        "date", "store_id", "sku_id", "stockout_risk", "risk_tier",
        "days_of_stock_left", "forecast_qty", "qty_sold", "stock_on_hand"
    ] if c in available_cols]

    df = pd.read_parquet(RISK_PATH, columns=wanted_cols)

    # Downcast numeric dtypes to shrink memory footprint
    for col in df.select_dtypes(include="float64").columns:
        df[col] = df[col].astype("float32")

    # Keep only the latest snapshot per store-sku (dashboard doesn't need
    # the full historical time series — that cuts 29M rows down drastically)
    if "date" in df.columns:
        df = df.sort_values("date").groupby(["store_id", "sku_id"], as_index=False).tail(1)

    return df

@st.cache_data(ttl=60)
def load_benchmark():
    if not os.path.exists(BENCHMARK_PATH):
        return None
    df = pd.read_csv(BENCHMARK_PATH, header=None,
                      names=["run_timestamp", "cpu_seconds", "gpu_seconds", "speedup_factor"])
    df["run_timestamp"] = pd.to_datetime(df["run_timestamp"], errors="coerce")
    return df

risk_df = load_risk()
bench_df = load_benchmark()

# ---------------------------------------------------------------------------
# GUARD: missing files
# ---------------------------------------------------------------------------
if risk_df is None:
    st.error(
        f"Could not find `{RISK_PATH}`. Make sure you've downloaded "
        f"`risk_scores.parquet` from Colab and placed it in `{DATA_DIR}/`."
    )
    st.stop()

# make sure risk_tier exists even if older pipeline runs didn't add it
if "risk_tier" not in risk_df.columns and "stockout_risk" in risk_df.columns:
    risk_df["risk_tier"] = risk_df["stockout_risk"].apply(
        lambda x: "CRITICAL" if x > 0.75 else ("WARNING" if x > 0.5 else "OK")
    )

# ---------------------------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

critical_count = (risk_df["risk_tier"] == "CRITICAL").sum() if "risk_tier" in risk_df else 0
warning_count = (risk_df["risk_tier"] == "WARNING").sum() if "risk_tier" in risk_df else 0
total_skus = len(risk_df)

col1.metric("Critical SKUs", int(critical_count))
col2.metric("Warning SKUs", int(warning_count))
col3.metric("Total SKU-Store Rows", f"{total_skus:,}")

if bench_df is not None and len(bench_df) > 0:
    latest = bench_df.sort_values("run_timestamp", ascending=False).iloc[0]
    col4.metric("Last GPU Speedup", f"{latest['speedup_factor']:.1f}x")
else:
    col4.metric("Last GPU Speedup", "n/a")

st.divider()

# ---------------------------------------------------------------------------
# TOP RISK TABLE
# ---------------------------------------------------------------------------
st.subheader("Top Risk Items")

display_cols = [c for c in [
    "store_id", "sku_id", "risk_tier", "stockout_risk",
    "days_of_stock_left", "forecast_qty"
] if c in risk_df.columns]

top_n = st.slider("Show top N riskiest SKU-store combos", 10, 100, 25)

st.dataframe(
    risk_df.sort_values("stockout_risk", ascending=False)
           .head(top_n)[display_cols],
    use_container_width=True
)

# ---------------------------------------------------------------------------
# HEATMAP BY STORE
# ---------------------------------------------------------------------------
st.subheader("Average Risk by Store")

if "store_id" in risk_df.columns:
    heat = (
        risk_df.groupby("store_id")["stockout_risk"]
               .mean()
               .reset_index()
               .sort_values("stockout_risk", ascending=False)
               .head(20)
    )
    fig = px.bar(
        heat, x="store_id", y="stockout_risk",
        color="stockout_risk", color_continuous_scale="Reds",
        title="Top 20 Stores by Average Stockout Risk"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# CPU vs GPU BENCHMARK CHART  <-- the acceleration proof
# ---------------------------------------------------------------------------
st.subheader("⚡ CPU vs GPU Processing Time")

if bench_df is not None and len(bench_df) > 0:
    melted = bench_df.melt(
        id_vars=["run_timestamp"],
        value_vars=["cpu_seconds", "gpu_seconds"],
        var_name="engine", value_name="seconds"
    )
    fig2 = px.bar(
        melted, x="run_timestamp", y="seconds", color="engine",
        barmode="group", title="Pipeline Runtime: CPU (pandas) vs GPU (cudf.pandas)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    latest = bench_df.sort_values("run_timestamp", ascending=False).iloc[0]
    st.success(
        f"Latest run: **{latest['cpu_seconds']:.1f}s (CPU)** → "
        f"**{latest['gpu_seconds']:.1f}s (GPU)** — "
        f"**{latest['speedup_factor']:.1f}x speedup** using NVIDIA cudf.pandas."
    )
else:
    st.info(
        "No benchmark data yet. Run the CPU and GPU pipelines, then log the "
        f"result to `{BENCHMARK_PATH}` (see `pipeline/log_benchmark.py`)."
    )

# ---------------------------------------------------------------------------
# GEMINI DAILY BRIEFING
# ---------------------------------------------------------------------------
st.subheader("🤖 AI Daily Briefing (Gemini)")

BRIEFING_PATH = os.path.join(DATA_DIR, "latest_briefing.txt")

def load_saved_briefing():
    if os.path.exists(BRIEFING_PATH):
        with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return None

def generate_new_briefing():
    """Regenerates the briefing live, right from the dashboard button."""
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY not set in .env"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    top = risk_df.sort_values("stockout_risk", ascending=False).head(15)
    cols = [c for c in ["store_id", "sku_id", "risk_tier", "stockout_risk", "days_of_stock_left"]
            if c in top.columns]
    data_str = top[cols].to_string(index=False)

    prompt = f"""
You are an autonomous inventory operations agent. Given this stockout risk data
(store, sku, risk tier, risk score, days of stock left), write a concise daily
briefing for a store operations manager:

1. Open with a one-line summary of overall inventory health today.
2. List the top 5-10 highest-risk items, grouped by store if possible, with
   days of stock left.
3. End with ONE clear recommended action.

Keep it under 200 words, plain English, no markdown headers.

Data:
{data_str}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        with open(BRIEFING_PATH, "w", encoding="utf-8") as f:
            f.write(text)
        return text, None
    except Exception as e:
        return None, str(e)


col_a, col_b = st.columns([3, 1])
with col_b:
    regenerate = st.button("🔄 Regenerate briefing", use_container_width=True)

if regenerate:
    with st.spinner("Asking Gemini to analyze current risk data..."):
        new_text, error = generate_new_briefing()
    if error:
        st.error(f"Could not generate briefing: {error}")
    else:
        st.session_state["briefing_text"] = new_text

briefing_text = st.session_state.get("briefing_text") or load_saved_briefing()

with col_a:
    if briefing_text:
        st.info(briefing_text)
    else:
        st.warning(
            "No briefing yet. Click 'Regenerate briefing' or run "
            "`python agent/run_briefing.py` first."
        )

# ---------------------------------------------------------------------------
# RAW DATA (optional expander for judges who want to inspect)
# ---------------------------------------------------------------------------
with st.expander("View raw risk_scores data"):
    st.dataframe(risk_df, use_container_width=True)