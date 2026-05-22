"""
run_pipeline.py
---------------
Orchestrates the full pipeline from raw data to model outputs.

Steps:
    1. Trigger Glue ETL job (raw CSV → processed Parquet)
    2. Wait for Glue job to complete
    3. Run PCA + KMeans scoring (Athena → outputs)

Usage:
    python run_pipeline.py
"""

import boto3
import time
from sagemaker.pca_kmeans import main as run_scoring

GLUE_JOB_NAME = "etl-delitos-observatory"

def run_glue_job():
    """Triggers the Glue ETL job and waits for completion."""
    client = boto3.client('glue', region_name='us-east-1')
    
    response = client.start_job_run(JobName=GLUE_JOB_NAME)
    job_run_id = response['JobRunId']
    print(f"Glue job started: {job_run_id}")

    # Wait for completion
    while True:
        status = client.get_job_run(
            JobName=GLUE_JOB_NAME,
            RunId=job_run_id
        )['JobRun']['JobRunState']
        
        print(f"Glue job status: {status}")
        
        if status == 'SUCCEEDED':
            print("Glue job completed successfully")
            break
        elif status in ['FAILED', 'ERROR', 'TIMEOUT']:
            raise Exception(f"Glue job failed with status: {status}")
        
        time.sleep(30)


def main():
    print("── Step 1: Running Glue ETL job ──────────────────────────")
    run_glue_job()
    
    print("\n── Step 2: Running PCA + KMeans scoring ──────────────────")
    run_scoring()
    
    print("\n✓ Full pipeline complete")


if __name__ == "__main__":
    main()