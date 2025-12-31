import os
import pandas as pd
import requests
import time # Added import
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

def fetch_bitcoin_price():
    """Fetches Bitcoin price with retry logic for rate limits."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur,gbp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            print("⚠️ Rate Limit Hit (429). Cooling down for 60 seconds...")
            time.sleep(60)
            return fetch_bitcoin_price() 
            
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def create_dataframe(price_data):
    """Creates a Pandas DataFrame from the price data."""
    if not price_data:
        return None
    
    df = pd.DataFrame([price_data])
    df['timestamp'] = pd.to_datetime('now', utc=True)
    return df


def load_to_bigquery(df, project_id, dataset_id, table_id):
    """
    Loads a DataFrame into a BigQuery table.
    Checks for dataset and table existence and creates them if they don't exist.
    """
    if df is None:
        print("DataFrame is empty, skipping BigQuery load.")
        return

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    # Check for dataset existence
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        print(f"Dataset {dataset_id} not found, creating it.")
        client.create_dataset(dataset_ref, exists_ok=True)

    table_ref = dataset_ref.table(table_id)

    # Define table schema
    schema = [
        bigquery.SchemaField("usd", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("eur", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("gbp", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Check for table existence
    try:
        client.get_table(table_ref)
        print(f"Table {table_id} already exists.")
    except NotFound:
        print(f"Table {table_id} not found, creating it.")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_APPEND",
    )

    try:
        print(f"Loading data into {project_id}.{dataset_id}.{table_id}...")
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        print(f"Successfully loaded {job.output_rows} rows.")
    except Exception as e:
        print(f"Error loading data to BigQuery: {e}")

def main():
    """Main ETL function."""
    print("Starting ETL job...")
    
    # Get configuration from environment variables
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BQ_DATASET")
    table_id = os.getenv("BQ_TABLE")

    if not all([project_id, dataset_id, table_id]):
        print("Error: Missing required environment variables (GCP_PROJECT_ID, BQ_DATASET, BQ_TABLE).")
        return

    # Loop for iterations with a delay
    iterations :int = 1
    for i in range(iterations):
        print(f"--- ETL Cycle {i+1}/{iterations} ---")
        # ETL Process
        price_data = fetch_bitcoin_price()
        df = create_dataframe(price_data)
        load_to_bigquery(df, project_id, dataset_id, table_id)
        
        if i < iterations - 1:
            print("Waiting for 1 minute before next cycle...")
            time.sleep(80)
    
    print("ETL job finished.")

if __name__ == "__main__":
    main()