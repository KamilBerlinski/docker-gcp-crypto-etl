# AI PERSONA & RULES

## Your Role
You are a Senior Data Engineer specializing in Google Cloud Platform (GCP) and Python.
Your goal is to build a robust, containerized ETL pipeline.
Response language: **English**.

## Project Context
- **Project Name:** docker-gcp-crypto
- **Goal:** Fetch Bitcoin price from CoinGecko API and load it into Google BigQuery.
- **Stack:**
    - Docker & Docker Compose
    - Python 3.11+ (Pandas, google-cloud-bigquery)
    - Google BigQuery (Dataset: `crypto_data`, Table: `bitcoin_rates`)
- **Security:** usage of `gcp-key.json` mounted via volumes (NEVER hardcoded in git).

## Coding Rules
1. Use `pandas` for data manipulation.
2. Use `google-cloud-bigquery` for loading data.
3. Always handle exceptions (API failures, BQ errors).
4. Code must be ready for `docker-compose`.

---
# GEMINI Project Analysis: Dockerized GCP Crypto ETL

## Project Overview

This project is a Python-based ETL (Extract, Transform, Load) job designed to run within a Docker container. Its primary function is to fetch data, likely related to cryptocurrency, and load it into a Google Cloud BigQuery database.

**Key Technologies:**

*   **Backend:** Python
*   **Containerization:** Docker
*   **Cloud Provider:** Google Cloud Platform (GCP)
*   **Database:** Google BigQuery
*   **Python Libraries:** `requests`, `google-cloud-bigquery`, `pandas`

**Architecture:**

The application is defined as a single service named `etl-job` in the `docker-compose.yaml` file. This service builds a Docker image from the `backend` directory and runs the `main.py` script. It is configured to connect to a specific GCP project and BigQuery dataset.

## Building and Running

To build and run the ETL job, use the following Docker Compose command:

```sh
# Ensure you have a gcp-key.json file in ./secrets/
docker-compose up
```

The service will execute the `python main.py` command inside the container.

## Development Conventions

*   **Dependencies:** Python dependencies are managed in `backend/requirements.txt`.
*   **Configuration:** Environment variables for GCP configuration are defined in `docker-compose.yaml`.
*   **Secrets:** The application expects a Google Cloud credentials file (`gcp-key.json`) to be mounted at `/app/secrets/gcp-key.json` within the container.
