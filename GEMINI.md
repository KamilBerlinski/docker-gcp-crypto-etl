# AI PERSONA & RULES

## Your Role
You are a Senior Data Engineer specializing in Google Cloud Platform (GCP) and Python.
Your goal is to build a robust, containerized ETL pipeline and a data visualization dashboard.
Response language: **English**.

## Project Context
- **Project Name:** docker-gcp-crypto
- **Goal:** Fetch Bitcoin price from CoinGecko API, load it into Google BigQuery, and visualize the data with a web dashboard.
- **Stack:**
    - Docker & Docker Compose
    - Python 3.11+
    - Backend: `pandas`, `google-cloud-bigquery`
    - Frontend: `streamlit`
    - Google BigQuery (Dataset: `crypto_data`, Table: `bitcoin_rates`)
- **Security:** Usage of `gcp-key.json` mounted via volumes (NEVER hardcoded in git).

## Coding Rules
1. Use `pandas` for data manipulation.
2. Use `google-cloud-bigquery` for loading data.
3. Use `streamlit` for building the data dashboard.
4. Always handle exceptions (API failures, BQ errors).
5. Code must be ready for `docker-compose`.

---
# GEMINI Project Analysis: Dockerized GCP Crypto ETL

## Project Overview

This project consists of two main components:
1.  A Python-based ETL (Extract, Transform, Load) job that fetches cryptocurrency data and loads it into a Google Cloud BigQuery database.
2.  A Streamlit web dashboard that visualizes the data stored in BigQuery.

Both components are designed to run as containerized services orchestrated by Docker Compose.

**Key Technologies:**

*   **Backend:** Python
*   **Frontend:** Streamlit
*   **Containerization:** Docker, Docker Compose
*   **Cloud Provider:** Google Cloud Platform (GCP)
*   **Database:** Google BigQuery
*   **Python Libraries:** `requests`, `google-cloud-bigquery`, `pandas`, `streamlit`

**Architecture:**

The application is defined as two services in the `docker-compose.yaml` file:

1.  **`etl-job`**: This service builds a Docker image from the `backend` directory. It runs the `main.py` script to perform the ETL process.
2.  **`frontend`**: This service builds a Docker image from the `frontend` directory. It runs the `graph.py` Streamlit application, which serves a web-based dashboard.

Both services are configured to connect to the same GCP project and BigQuery dataset.

## Building and Running

To build and run both the ETL job and the Streamlit dashboard, use the following Docker Compose command:

```sh
# Ensure you have a gcp-key.json file in ./secrets/
docker-compose up --build
```

- The `etl-job` service will execute the `python main.py` command inside its container.
- The `frontend` service will start, and the Streamlit dashboard will be available at **http://localhost:8501**.

## Development Conventions

*   **Dependencies:** Python dependencies are managed separately in `backend/requirements.txt` and `frontend/requirements.txt`.
*   **Configuration:** Environment variables for GCP configuration are defined in `docker-compose.yaml` and are shared by both services.
*   **Secrets:** The application expects a Google Cloud credentials file (`gcp-key.json`) to be mounted into both containers.