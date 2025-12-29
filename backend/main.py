import os
import pandas as pd
import requests
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

def fetch_bitcoin_price():
    """Fetches Bitcoin price from the CoinGecko API."""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur,gbp")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data['bitcoin']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinGecko API: {e}")
        return None

def create_dataframe(price_data):
    """Creates a Pandas DataFrame from the price data."""
    if not price_data:
        return None
    
    df = pd.DataFrame([price_data])
    df['timestamp'] = pd.to_datetime('now', utc=True)
    return df

def load_to_bigquery(df, project_id, dataset_id, table_id):
    """Loads a DataFrame into a BigQuery table."""
    if df is None:
        print("DataFrame is empty, skipping BigQuery load.")
        return

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        print(f"Dataset {dataset_id} not found, creating it.")
        client.create_dataset(dataset_ref, exists_ok=True)

    # Define table schema
    schema = [
        bigquery.SchemaField("usd", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("eur", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("gbp", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

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

    # ETL Process
    price_data = fetch_bitcoin_price()
    df = create_dataframe(price_data)
    load_to_bigquery(df, project_id, dataset_id, table_id)
    
    print("ETL job finished.")

if __name__ == "__main__":
    main()