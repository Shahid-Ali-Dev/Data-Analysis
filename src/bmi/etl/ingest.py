from __future__ import annotations
import argparse
from pathlib import Path
import duckdb
import pandas as pd
from bmi.utils.config import SETTINGS, ROOT

def create_tables(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS mandi_prices (
        date DATE,
        state VARCHAR,
        district VARCHAR,
        market VARCHAR,
        commodity VARCHAR,
        variety VARCHAR,
        min_price DOUBLE,
        max_price DOUBLE,
        modal_price DOUBLE,
        arrivals_tonnes DOUBLE
    );
    """)

def ingest_sample(con):
    sample_path = SETTINGS.data_dir / "sample_agmarknet_onion_nashik.csv"
    df = pd.read_csv(sample_path, parse_dates=["date"])
    con.execute("DELETE FROM mandi_prices WHERE state='Maharashtra' AND market='Nashik' AND commodity='Onion'")
    con.execute("INSERT INTO mandi_prices SELECT * FROM df")
    print(f"Ingested {len(df)} rows from {sample_path}")

def main(sample: bool):
    SETTINGS.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(SETTINGS.duckdb_path))
    create_tables(con)
    if sample:
        ingest_sample(con)
    print(f"DuckDB at: {SETTINGS.duckdb_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Load bundled synthetic sample")
    args = parser.parse_args()
    main(sample=args.sample)
