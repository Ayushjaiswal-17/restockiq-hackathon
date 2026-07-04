from google.cloud import storage
from pipeline.config import GCS_BUCKET

def upload(local_path, blob_name):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} -> gs://{GCS_BUCKET}/{blob_name}")

if __name__ == "__main__":
    upload("data/sample/pos_transactions.csv", "pos_transactions.csv")
    upload("data/sample/copurchase_edges.csv", "copurchase_edges.csv")