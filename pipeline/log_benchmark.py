"""
Usage:
    python pipeline/log_benchmark.py <cpu_seconds> <gpu_seconds>

Example:
    python pipeline/log_benchmark.py 120.43 18.76
"""
import sys
import csv
import os
from datetime import datetime

BENCHMARK_PATH = "data/sample/benchmark_log.csv"


def log(cpu_time: float, gpu_time: float, path: str = BENCHMARK_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    speedup = cpu_time / gpu_time if gpu_time else 0
    file_exists = os.path.exists(path)

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), cpu_time, gpu_time, speedup])

    print(f"Logged: CPU={cpu_time}s GPU={gpu_time}s Speedup={speedup:.2f}x -> {path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pipeline/log_benchmark.py <cpu_seconds> <gpu_seconds>")
        sys.exit(1)

    cpu_seconds = float(sys.argv[1])
    gpu_seconds = float(sys.argv[2])
    log(cpu_seconds, gpu_seconds)