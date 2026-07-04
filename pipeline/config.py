import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data/sample"
POS_CLEAN_PATH = f"{DATA_DIR}/pos_clean.parquet"
RISK_OUTPUT_PATH = f"{DATA_DIR}/risk_scores.parquet"
BENCHMARK_LOG_PATH = f"{DATA_DIR}/benchmark_log.csv"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ROLLING_WINDOW_DAYS = 7
RISK_HIGH_THRESHOLD = 0.55  # tuned down based on your test run