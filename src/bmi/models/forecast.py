from __future__ import annotations
import mlflow
import duckdb
import pandas as pd
from pathlib import Path
from bmi.utils.config import SETTINGS

FEATURES = ["doy","dow","month","lag1","lag7","lag14","r7","r14","arrivals_tonnes","delta"]

def latest_model_uri(h):
    exp = f"BMI-PriceForecast-H{h}"
    client = mlflow.tracking.MlflowClient(tracking_uri=SETTINGS.mlflow_uri)
    exp_obj = client.get_experiment_by_name(exp)
    if exp_obj is None:
        raise SystemExit(f"No experiment found: {exp}")
    runs = client.search_runs(exp_obj.experiment_id, order_by=["metrics.mape_in_sample ASC"], max_results=1)
    if not runs:
        raise SystemExit(f"No runs for {exp}")
    return runs[0].info.run_id, f"runs:/{runs[0].info.run_id}/model"

def generate_forecast():
    con = duckdb.connect(str(SETTINGS.duckdb_path))
    df = con.execute("SELECT * FROM features ORDER BY date").df().copy()
    # Use last available row as seed for features; in production you'd roll-forward with predicted lags
    last = df.iloc[-1:]
    out_rows = []
    mlflow.set_tracking_uri(SETTINGS.mlflow_uri)
    for h in (1,7,14):
        run_id, uri = latest_model_uri(h)
        model = mlflow.sklearn.load_model(uri)
        X = last[FEATURES]
        yhat = float(model.predict(X)[0])
        out_rows.append({"horizon": h, "forecast_price": yhat})
    out = pd.DataFrame(out_rows)
    out["generated_at"] = pd.Timestamp.utcnow()
    con.execute("CREATE OR REPLACE TABLE forecasts AS SELECT * FROM out")
    print(out)

if __name__ == "__main__":
    generate_forecast()
