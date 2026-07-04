# 🚨 RestockIQ — Autonomous Inventory Command Center

A GPU-accelerated data intelligence tool that helps retail store managers prevent stockouts before they happen.

Built for the **Google Cloud x NVIDIA Hackathon**.

---

## The Problem

Retail and grocery store managers are responsible for tracking inventory across thousands of SKU-store combinations. Today, this is done manually in spreadsheets or through slow end-of-day batch reports — by the time a manager sees an item is about to run out, it's often too late to reorder in time.

**The decision this tool supports:**
> "Which of my SKUs across all my stores will stock out in the next 1–3 days, and what should I do about it right now?"

---

## What It Does

1. **Ingests** 29.2 million rows of synthetic POS transaction data (50 stores × 2,000 SKUs × 2 years)
2. **Cleans** it with a local SQL transformation layer (DuckDB — mirrors a BigQuery pattern)
3. **Computes** rolling demand features, stockout urgency, demand-velocity trends, and anomaly signals
4. **Accelerates** the entire feature-engineering pipeline with **NVIDIA cudf.pandas** — same pandas code, GPU-executed
5. **Visualizes** results in a live Streamlit dashboard — risk rankings, store heatmap, and a CPU-vs-GPU benchmark
6. **Summarizes** the situation with **Gemini**, turning a 100,000-row risk table into a plain-English daily briefing with one clear recommended action

---

## ⚡ The Acceleration Story

We benchmarked the exact same pipeline on the same 29.2M rows — CPU (pandas) vs GPU (cudf.pandas) — with a **one-line code change**: `cudf.pandas.install()`.

| Engine | Time |
|---|---|
| CPU (pandas) | 120.4 seconds |
| GPU (NVIDIA cudf.pandas) | 18.8 seconds |
| **Speedup** | **6.4x** |

**Honest note:** our first benchmark at smaller scale (2.9M rows) actually showed GPU running *slower* than CPU (46s vs 35s), due to kernel warmup overhead and a non-vectorized Python lambda inside a `.groupby().rolling()` call. We fixed the vectorization and scaled the dataset up to 29.2M rows — that's when the GPU advantage became clear and consistent. We think this is a more honest and instructive result than a cherry-picked number.

---

## Architecture

```
Synthetic POS data (29.2M rows, CSV)
        │
        ▼
Local SQL cleaning layer (DuckDB)
        │
        ▼
Feature engineering: rolling demand, velocity, days-of-stock-left
        │
        ├── CPU path (pandas)              ──┐
        └── GPU path (NVIDIA cudf.pandas)     │──► Benchmark comparison
                    │                         │
                    ▼                         │
        Risk fusion (stockout urgency +       │
        anomaly signal + velocity trend)      │
                    │                         │
                    ▼                         ▼
            risk_scores.parquet ──► Streamlit Dashboard
                    │                 - Risk ranking table
                    │                 - Store risk heatmap
                    │                 - CPU vs GPU benchmark chart
                    ▼
        Gemini API (gemini-2.5-flash)
                    │
                    ▼
        Plain-English daily briefing + one recommended action
```

---

## Tech Stack

**NVIDIA acceleration layer**
- `cudf.pandas` — drop-in GPU acceleration for pandas operations
- Executed on an NVIDIA T4 GPU (Google Colab)

**Data & application layer**
- DuckDB — local SQL transformation layer (BigQuery-equivalent pattern)
- Streamlit + Plotly — interactive dashboard
- Gemini API (`gemini-2.5-flash`) — natural-language decision briefing

> This pipeline is designed to map directly onto **BigQuery + Cloud Storage + a GPU VM on Google Cloud** with no structural code changes — local-equivalent tools (DuckDB, local Parquet, Colab GPU) were used during development due to a billing constraint on our GCP project during the hackathon window.

---

## Project Structure

```
restockiq/
├── data/
│   ├── generate_data.py            # generates synthetic POS transaction data
│   └── generate_copurchase_graph.py
├── ingestion/
│   └── clean_local.py              # DuckDB-based cleaning (BigQuery-equivalent pattern)
├── pipeline/
│   ├── config.py
│   ├── features.py                 # rolling demand, velocity features
│   ├── anomaly_detection.py
│   ├── risk_fusion.py              # combines signals into final risk score
│   ├── forecast_cuml.py
│   ├── run_cpu_baseline.py         # CPU (pandas) benchmark
│   ├── run_gpu_pipeline.py         # GPU (cudf.pandas) benchmark — run on Colab/GPU VM
│   └── log_benchmark.py            # logs CPU/GPU timing for the dashboard
├── agent/
│   └── run_briefing.py             # Gemini-powered daily briefing generator
├── dashboard/
│   └── streamlit_app.py            # live dashboard (risk table, heatmap, benchmark, AI briefing)
└── README.md
```

---

## Setup & Running Locally

Data files are excluded from this repo due to size (GitHub's 100MB limit). Regenerate them locally:

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate the dataset
```bash
python data/generate_data.py
python ingestion/clean_local.py
```

### 3. Run the CPU baseline
```bash
python -m pipeline.run_cpu_baseline
```

### 4. Run the GPU pipeline (requires an NVIDIA GPU — Colab T4 works well)
Upload `data/sample/pos_clean.parquet` to a Colab notebook with a T4 GPU runtime, install RAPIDS:
```bash
pip install cudf-cu12 cuml-cu12 cugraph-cu12 --extra-index-url=https://pypi.nvidia.com
```
Then run the equivalent of `pipeline/run_gpu_pipeline.py` and download `risk_scores.parquet` back into `data/sample/`.

### 5. Log the benchmark
```bash
python pipeline/log_benchmark.py <cpu_seconds> <gpu_seconds>
```

### 6. Set up Gemini
Get a free API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey), then create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### 7. Generate the AI briefing
```bash
python agent/run_briefing.py
```

### 8. Launch the dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

---

## Live Links

- **Deployed dashboard:** [add your Streamlit Cloud link]
- **Demo video:** [add your video link]
- **Submission deck:** `RestockIQ_Submission.pptx` (in repo root)

---

## What We'd Build Next

- Real-time streaming ingestion via Cloud Pub/Sub instead of batch snapshots
- Substitution-recommendation engine using NVIDIA cuGraph on co-purchase data
- Human-in-the-loop purchase order approval workflow
- Full deployment on BigQuery + GKE with a provisioned GPU node pool for continuous scoring

---

## Team

[Add your name(s) here]
