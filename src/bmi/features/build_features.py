from __future__ import annotations
import duckdb
import pandas as pd
from bmi.utils.config import SETTINGS

def build_features():
    con = duckdb.connect(str(SETTINGS.duckdb_path))
    df = con.execute("SELECT * FROM mandi_prices ORDER BY date").df()
    if df.empty:
        raise SystemExit("No data found in mandi_prices; run `make ingest` first.")

    # Basic time features
    df["doy"] = df["date"].dt.dayofyear
    df["dow"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    # Lags and rolling features per group
    df = df.sort_values(["state", "market", "commodity", "date"]).copy()
    gcols = ["state", "market", "commodity"]
    df["lag1"] = df.groupby(gcols)["modal_price"].shift(1)
    df["lag7"] = df.groupby(gcols)["modal_price"].shift(7)
    df["lag14"] = df.groupby(gcols)["modal_price"].shift(14)
    df["r7"] = df.groupby(gcols)["modal_price"].rolling(7).mean().reset_index(level=gcols, drop=True)
    df["r14"] = df.groupby(gcols)["modal_price"].rolling(14).mean().reset_index(level=gcols, drop=True)
    df["delta"] = df["modal_price"] - df["lag1"]

    # Train/target setup: predict modal_price at horizon h by shifting backwards
    for h in (1, 7, 14):
        df[f"target_h{h}"] = df.groupby(gcols)["modal_price"].shift(-h)

    # Write features to DuckDB
    con.execute("CREATE OR REPLACE TABLE features AS SELECT * FROM df")
    print("Built features → table 'features'")

if __name__ == "__main__":
    build_features()
