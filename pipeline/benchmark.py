import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from pipeline.config import GCP_PROJECT_ID, TABLE_BENCHMARK
import run_cpu_baseline
import run_gpu_pipeline

def log_benchmark():
    cpu_time = run_cpu_baseline.run()
    gpu_time = run_gpu_pipeline.run()
    speedup = cpu_time / gpu_time

    row = pd.DataFrame([{
        "run_timestamp": datetime.utcnow(),
        "cpu_seconds": cpu_time,
        "gpu_seconds": gpu_time,
        "speedup_factor": speedup,
    }])

    client = bigquery.Client(project=GCP_PROJECT_ID)
    client.load_table_from_dataframe(row, TABLE_BENCHMARK).result()
    print(f"Speedup: {speedup:.1f}x  (CPU {cpu_time:.1f}s -> GPU {gpu_time:.1f}s)")

if __name__ == "__main__":
    log_benchmark()