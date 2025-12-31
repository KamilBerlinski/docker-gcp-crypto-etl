import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery

# --- Configuration ---
# Fetch GCP Project ID from environment variables
try:
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    BQ_DATASET = os.environ["BQ_DATASET"]
    BQ_TABLE = os.environ["BQ_TABLE"]
except KeyError:
    st.error(
        "Required environment variables are not set: "
        "GCP_PROJECT_ID, BQ_DATASET, BQ_TABLE"
    )
    st.stop()

# --- BigQuery Data Fetching ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_data_from_bigquery():
    """Fetches Bitcoin price data from the BigQuery table."""
    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        query = f"""
            SELECT
                timestamp,
                usd,
                eur,
                gbp
            FROM
                `{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
            ORDER BY
                timestamp DESC
        """
        st.info("Fetching the latest data from BigQuery...")
        query_job = client.query(query)
        df = query_job.to_dataframe()
        st.success("Data fetched successfully!")
        return df
    except Exception as e:
        st.error(f"Failed to fetch data from BigQuery: {e}")
        return pd.DataFrame() # Return empty dataframe on error

# --- Streamlit UI ---
st.set_page_config(page_title="Bitcoin Price Dashboard", layout="wide")

# --- Header ---
st.title("_Bitcoin_ Price :red[Dashboard] :chart_with_upwards_trend:")
st.markdown("Live data sourced from Google BigQuery")

# --- Refresh Button ---
if st.button("Refresh Data", type="primary"):
    # Clear the cache to force a re-fetch of data
    st.cache_data.clear()
    st.rerun()

# --- Load Data ---
data = fetch_data_from_bigquery()

if data.empty:
    st.warning("No data available to display. Please ensure the ETL job has run at least once.")
else:
    # --- Data Display ---
    st.header("Price Chart (USD)")
    
    # Prepare data for charting (ensure timestamp is index)
    chart_data = data.copy().set_index('timestamp')
    
    st.line_chart(chart_data['usd'])

    st.header("Latest Price Data")
    st.dataframe(data.head(10), use_container_width=True)

    with st.expander("Full Data History"):
        st.dataframe(data, use_container_width=True)

# --- Sidebar Info ---
st.sidebar.header("About")
st.sidebar.info(
    "This dashboard visualizes Bitcoin price data stored in Google BigQuery. "
    "The data is collected by a separate ETL process."
)
st.sidebar.header("Configuration")
st.sidebar.write(f"**Project ID:** `{GCP_PROJECT_ID}`")
st.sidebar.write(f"**Dataset:** `{BQ_DATASET}`")
st.sidebar.write(f"**Table:** `{BQ_TABLE}`")
