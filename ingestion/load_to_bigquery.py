from google.cloud import bigquery
from pipeline.config import GCP_PROJECT_ID, BQ_DATASET, GCS_BUCKET

def load_table(gcs_path, table_id):
    client = bigquery.Client(project=GCP_PROJECT_ID)
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,
        skip_leading_rows=1,
    )
    uri = f"gs://{GCS_BUCKET}/{gcs_path}"
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    print(f"Loaded {gcs_path} -> {table_id}")

if __name__ == "__main__":
    load_table("pos_transactions.csv", f"{GCP_PROJECT_ID}.{BQ_DATASET}.pos_transactions")
    load_table("copurchase_edges.csv", f"{GCP_PROJECT_ID}.{BQ_DATASET}.copurchase_edges")