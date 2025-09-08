import os
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st
from bmi.utils.config import SETTINGS

st.set_page_config(page_title="BharatMandi Intelligence", layout="wide")

st.title("🇮🇳 BharatMandi Intelligence — Price Nowcasting & Forecasting")
st.caption("Synthetic demo: Nashik onion; plug real connectors in `src/bmi/etl`")

con = duckdb.connect(str(SETTINGS.duckdb_path))
df = con.execute("SELECT * FROM mandi_prices ORDER BY date").df()
feat = con.execute("SELECT * FROM features ORDER BY date").df() if con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='features'").fetchone()[0] else None
fc = con.execute("SELECT * FROM forecasts").df() if con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='forecasts'").fetchone()[0] else None

col1, col2 = st.columns([2,1])
with col1:
    st.subheader("Modal Price (₹/quintal)")
    fig = px.line(df, x="date", y="modal_price", title="Historical Prices")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.metric("Latest Price (₹/qtl)", f"{df['modal_price'].iloc[-1]:,.0f}")
    st.metric("Arrivals (tonnes)", f"{df['arrivals_tonnes'].iloc[-1]:,.0f}")

if fc is not None and not fc.empty:
    st.subheader("Forecasts")
    st.dataframe(fc)

st.write("---")
st.write("**How to extend:** Add real ETL in `src/bmi/etl` and re-run `make ingest → features → train → forecast`.")
