# EDGAR Filings — Data Cleaning & Visualization

A lightweight, high-performance data cleaning and visualization toolkit for SEC EDGAR filings built with Python, Dask, Pydantic, MongoDB, and Streamlit.

This project ingests EDGAR master-index and filing data, standardizes and validates schemas, computes production-ready aggregations (gold layer), and provides an interactive Streamlit dashboard to explore cleaned filings and analytics.

## Features
- **Schema validation & type coercion** (Pydantic + Dask/pandas)
- Cleans numeric columns (prices, amounts), date columns, and boolean flags
- Normalizes text columns and removes invalid entries (e.g., missing CIKs)
- Deduplication and ingestion safeguards
- Computes production aggregations (Gold layer):
  - **Agg1:** Monthly filings by form (collection: `gold_filings_by_form_month`)
  - **Agg2:** Forms by year (collection: `gold_forms_by_year`)
  - **Agg3:** Top filers and 10-K specific aggregations (collections: `gold_top_ciks`, `gold_10k_top_ciks`, `gold_10k_recent`)
- Streamlit dashboard for filtering, charting, and viewing cleaned data and aggregations

## Installation of Required Libraries
Install project dependencies (uses `uv` for environment management):

```bash
uv sync --all-extras
```

> Tip: Check `pyproject.toml` for exact dependency versions.

## Environment variables (`.env`)
Create a `.env` at the repository root (do not commit it):

```text
cp .env.example .env
# then edit .env to include:
MONGO_URI="<your mongodb connection string>"
MONGO_DB="edgar"
SEC_USER_AGENT="Your Name your.email@domain"
EDGAR_DATA_DIR="data/edgar_cache"
```

The Streamlit app reads `MONGO_URI` strictly from `.env` and will fail fast with a clear error if it is missing or the connection cannot be established.

## Running the Pipeline
Important: global arguments (if any) are passed before the command when using `uv`.

### 1) Start MongoDB (Docker Compose)
```bash
docker compose up -d
```

Verify replica set (if running the Docker-based RS):
```bash
docker exec -it mongo1 mongosh --eval "rs.status()"
```

### 2) Install Dependencies
Install project dependencies before running the pipeline:
```bash
uv sync --all-extras
```

### 3) Ingest (raw layer)
```bash
PYTHONPATH=src uv run python -m edgar_pipeline.cli ingest --from-year 2025 --to-year 2025
```

### 4) Clean & Validate (clean layer)
```bash
PYTHONPATH=src uv run python -m edgar_pipeline.cli clean
```

### 5) Build Gold Aggregations
```bash
PYTHONPATH=src uv run python -m edgar_pipeline.cli gold
```

### 6) Run Streamlit Dashboard
```bash
streamlit run streamlit_app/app.py
# open http://localhost:8501 in your browser
```

## Library Requirements
- dask[dataframe]
- pandas
- pyarrow
- pymongo
- pydantic
- python-dotenv
- requests
- streamlit
- certifi

(See `pyproject.toml` for full list and pinned versions.)

## Project Structure
```
edgar-mongo-bigdata/
├─ data/                       # EDGAR master index and cached filings
├─ docker/
│  └─ mongo-init/              # Mongo init scripts and indexes
├─ diagrams/                   # Architecture diagrams (Mermaid)
├─ streamlit_app/
│  └─ app.py                   # Streamlit dashboard
├─ src/
│  └─ edgar_pipeline/          # Pipeline code (ingest, clean, aggregate, enrich)
├─ tests/                      # Unit tests (pytest)
├─ pyproject.toml
├─ docker-compose.yml
├─ .env.example                # Example env file (copy to .env)
├─ README.md
└─ uv.lock
```

## Additional Usage
Run Streamlit in development mode (auto-reload on save):

```bash
streamlit run streamlit_app/app.py --server.runOnSave true
```

Run tests and type checking:

```bash
uv run pytest
uv run mypy src
```

## Contribution
- Pull requests and suggestions are welcome ✅
- Please open an issue before submitting large or breaking changes

---