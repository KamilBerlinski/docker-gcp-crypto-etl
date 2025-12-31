# docker-gcp-crypto

This project implements a containerized, multi-service application using Docker and Python. It consists of:
1.  **An ETL Pipeline**: A backend service that periodically fetches Bitcoin exchange rates from the CoinGecko API, processes the data with Pandas, and loads it into a Google BigQuery table.
2.  **A Data Dashboard**: A frontend Streamlit service that visualizes the price history stored in BigQuery.

Configuration for both services (GCP Project ID, dataset, table) is managed via environment variables in a `docker-compose.yaml` file. Authentication to GCP is handled securely through a mounted service account key file.

## Project Workflow

This section describes the end-to-end process, from data ingestion by the backend to visualization by the frontend.

### Workflow Diagram

```mermaid
graph TD
    subgraph "User's Local Machine"
        A[User runs `docker-compose up --build`] --> B{Docker Engine};
        U[User accesses http://localhost:8501] --> FE_SVC[Frontend Service];
    end

    subgraph "Docker Environment"
        B -- reads --> C[docker-compose.yaml];
        C -- defines --> D[ETL Job Service];
        C -- defines --> FE_SVC[Frontend Service];

        D -- builds from --> E[backend/Dockerfile];
        D -- mounts --> F[secrets/gcp-key.json];
        D -- runs --> BE_Container[ETL Container];

        FE_SVC -- builds from --> FE_DF[frontend/Dockerfile];
        FE_SVC -- mounts --> F;
        FE_SVC -- runs --> FE_Container[Frontend Container];
    end

    subgraph "Backend ETL Container"
        BE_Container -- executes --> H[python main.py];
        H -- HTTP GET --> I[CoinGecko API];
        I -- returns Bitcoin data --> H;
        H -- processes data with --> J[Pandas DataFrame];
        J -- loads data into --> K[Google BigQuery Client];
        F -- authenticates --> K;
        K -- writes to --> L[BigQuery Table: bitcoin_rates];
    end

    subgraph "Frontend Dashboard Container"
        FE_Container -- runs --> FE_App[streamlit run graph.py];
        FE_App -- reads data from --> L;
    end

    subgraph "External Services"
        I[CoinGecko API];
        L[Google BigQuery];
    end
```

### Explanation

#### Backend: ETL Job
1.  **User Interaction**: The process starts when the user runs `docker-compose up`.
2.  **Docker Compose**: Docker Compose reads the `docker-compose.yaml` file and starts the defined services.
3.  **ETL Job Service**: It builds and runs the `etl-job` container from the `backend/Dockerfile`.
4.  **Secret Mounting**: A `gcp-key.json` file is securely mounted into the container for authentication.
5.  **Data Fetching (Extract)**: The container's `main.py` script calls the CoinGecko API to get Bitcoin prices.
6.  **Data Processing (Transform)**: The raw data is structured into a Pandas DataFrame.
7.  **Data Loading (Load)**: The script authenticates to Google Cloud and loads the DataFrame into the `bitcoin_rates` table in BigQuery.

#### Frontend: Dashboard
8.  **Frontend Service**: Docker Compose also builds and runs the `frontend` container, which starts the Streamlit application.
9.  **User Access**: The user navigates to `http://localhost:8501` in their browser.
10. **Data Visualization**: The Streamlit app queries the same BigQuery table, fetches the historical price data, and displays it in an interactive chart and a table.
11. **Caching**: The data is cached by Streamlit to prevent excessive queries to BigQuery, with a "Refresh" button to manually fetch the latest data.