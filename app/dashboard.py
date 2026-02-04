import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Gold & Silver Dashboard", layout="wide")

DATA_PATH = os.path.join("data", "portfolio_daily.csv")

@st.cache_data
def load_portfolio(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    if "Date" not in df.columns:
        raise ValueError("portfolio_daily.csv must have a 'Date' column")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df

st.title("Gold & Silver Simulator Dashboard")

# ===== Load data =====
try:
    df = load_portfolio(DATA_PATH)
except Exception as e:
    st.error(str(e))
    st.stop()

# ===== Sidebar filters =====
st.sidebar.header("Filters")
min_d = df["Date"].min().date()
max_d = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_d, max_d),
    min_value=min_d,
    max_value=max_d,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = pd.to_datetime(min_d)
    end_date = pd.to_datetime(max_d)

df_f = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

# ===== KPI cards =====
c1, c2, c3, c4 = st.columns(4)

def last_val(col: str):
    return df_f[col].iloc[-1] if (col in df_f.columns and len(df_f) > 0) else None

total_value = last_val("total_value")
cash = last_val("cash")
gold_value = last_val("gold_value")
silver_value = last_val("silver_value")

c1.metric("Total Value", f"${total_value:,.2f}" if total_value is not None else "—")
c2.metric("Cash", f"${cash:,.2f}" if cash is not None else "—")
c3.metric("Gold Value", f"${gold_value:,.2f}" if gold_value is not None else "—")
c4.metric("Silver Value", f"${silver_value:,.2f}" if silver_value is not None else "—")

st.divider()

# ===== Charts =====
left, right = st.columns(2)

with left:
    st.subheader("Total Value Over Time")
    if {"Date", "total_value"}.issubset(df_f.columns):
        fig = px.line(df_f, x="Date", y="total_value")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need columns: Date, total_value")

with right:
    st.subheader("Asset Breakdown")
    needed = {"Date", "gold_value", "silver_value"}
    if needed.issubset(df_f.columns):
        long_df = df_f.melt(
            id_vars=["Date"],
            value_vars=["gold_value", "silver_value"],
            var_name="asset",
            value_name="value",
        )
        fig = px.area(long_df, x="Date", y="value", color="asset")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need columns: Date, gold_value, silver_value")

st.divider()

st.subheader("Data Preview")
st.dataframe(df_f, use_container_width=True)