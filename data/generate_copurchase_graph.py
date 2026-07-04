import pandas as pd
import numpy as np

np.random.seed(7)
N_SKUS = 2000
N_EDGES = 15000

def generate():
    src = np.random.randint(0, N_SKUS, N_EDGES)
    dst = np.random.randint(0, N_SKUS, N_EDGES)
    weight = np.random.randint(1, 50, N_EDGES)  # co-purchase frequency
    df = pd.DataFrame({
        "src_sku": [f"sku_{i}" for i in src],
        "dst_sku": [f"sku_{i}" for i in dst],
        "weight": weight
    })
    df = df[df.src_sku != df.dst_sku]
    df.to_csv("data/sample/copurchase_edges.csv", index=False)
    print(f"Generated {len(df):,} co-purchase edges")

if __name__ == "__main__":
    generate()