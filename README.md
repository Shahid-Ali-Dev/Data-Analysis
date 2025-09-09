# 🏪 BharatMandi Intelligence — Commodity Price Nowcasting & Forecasting (India)

**Goal:** Build an industry-grade system that ingests all-India mandi price data (e.g., Agmarknet),
enriches with weather, seasonality & events, then **nowcasts and forecasts 1–14 days ahead**
for commodities like onion/tomato/potato. Outputs actionable **price anomaly alerts** and an
interactive **Streamlit** dashboard for stakeholders (retailers, traders, policymakers).

## Features
- **ETL:** Modular connectors (Agmarknet-style endpoints) → DuckDB data lake
- **Feature store:** Lagged prices, rolling stats, holiday/festival flags, weather joins
- **Models:** Gradient boosting (LightGBM/XGBoost) + SARIMAX baselines, per-commodity
- **Hyperparameter tuning:** Optuna
- **Experiment tracking:** MLflow
- **Orchestration:** Prefect flows for daily ingest → train → forecast → publish
- **App:** Streamlit dashboard (state/mandi/commodity drilldowns, forecast bands, alerts)
- **Packaging:** `pyproject.toml`, tests, pre-commit hooks, Docker

> Ships with a **tiny synthetic sample** (Nashik onion) so the pipeline runs offline.

## Repo Structure
```
bharatmandi-intelligence/
├─ app/                    # Streamlit app
├─ data/                   # Data lake (DuckDB, parquet, sample CSV)
├─ notebooks/              # Exploratory notebooks
├─ src/bmi/                # Python package
│  ├─ etl/                 # Data ingestion
│  ├─ features/            # Feature engineering
│  ├─ models/              # Training / inference
│  ├─ orchestration/       # Prefect flows
│  └─ utils/               # Config, logging
├─ tests/                  # Unit tests
├─ pyproject.toml
├─ requirements.txt
├─ Makefile
├─ Dockerfile
└─ .env.example
```

## Quickstart
```bash
# 1) Create & activate venv (Windows PowerShell shown)
python -m venv .venv
. .venv/Scripts/Activate.ps1        # Linux/Mac: source .venv/bin/activate

# 2) Install
pip install -U pip
pip install -r requirements.txt

# 3) First run – uses the synthetic sample
make ingest   # loads sample CSV into DuckDB and builds features
make train    # trains LightGBM model and logs to MLflow
make forecast # produces 14-day forecasts
make app      # launches Streamlit dashboard
# (Optional) make mlflow  # launches MLflow UI
```

## Configuration
- Copy `.env.example` → `.env` to override defaults.
- Edit `config.yaml` for commodities, states, target horizons, alert thresholds.

## Data Sources (intended)
- Agmarknet mandi prices (arrivals, modal/min/max)
- IMD weather summaries (rainfall/temperature) or open sources
- Indian holiday/festival calendar
*(Only synthetic data is bundled; connectors are stubbed for you to plug credentials.)*

## Production Notes
- Containerize with Docker; deploy Streamlit + DuckDB read-only
- Schedule daily Prefect flows (e.g., Cron on a small VM)
- Persist MLflow to a mounted volume or S3 compatible storage
- Add RBAC/auth if exposed to the internet

---

© 2025 BharatMandi Intelligence. MIT License.
