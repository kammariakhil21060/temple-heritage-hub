import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import get_all_temples, get_all_contributions

# Streamlit page setup
st.set_page_config(page_title="Heritage Statistics", page_icon="📈", layout="wide")

st.title("📈 Heritage Statistics")
st.markdown("Analytics and insights about temple heritage documentation activity")

# Load data
temples = get_all_temples()
contributions = get_all_contributions()

# Convert to DataFrame
df_temples = pd.DataFrame(temples)
df_contribs = pd.DataFrame(contributions)

# Ensure required columns exist (avoid KeyError)
for df, required_cols in [
    (df_temples, ["id", "name", "location", "state", "district", "date_documented"]),
    (df_contribs, ["id", "user_id", "temple_id", "timestamp"]),
]:
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

# Convert date columns to datetime
if not df_temples.empty:
    df_temples["date_documented"] = pd.to_datetime(df_temples["date_documented"], errors="coerce")
if not df_contribs.empty:
    df_contribs["timestamp"] = pd.to_datetime(df_contribs["timestamp"], errors="coerce")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Temples", len(df_temples))
col2.metric("Total Contributions", len(df_contribs))
if not df_contribs.empty:
    active_users = df_contribs["user_id"].nunique()
else:
    active_users = 0
col3.metric("Active Contributors", active_users)

# Monthly contributions chart
if not df_contribs.empty:
    df_contribs["Month"] = df_contribs["timestamp"].dt.to_period("M")
    monthly_data = df_contribs.groupby("Month").size().reset_index(name="Contributions")
    monthly_data["Month"] = monthly_data["Month"].astype(str)

    fig_monthly = px.bar(
        monthly_data,
        x="Month",
        y="Contributions",
        title="📅 Monthly Contributions",
        labels={"Contributions": "Number of Contributions"},
        color="Contributions",
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
else:
    st.info("No contributions data available for monthly chart.")

# State-wise temples chart
if not df_temples.empty:
    state_data = df_temples.groupby("state").size().reset_index(name="Temple Count")
    fig_state = px.pie(
        state_data,
        names="state",
        values="Temple Count",
        title="🗺️ Temples by State",
        hole=0.3,
    )
    st.plotly_chart(fig_state, use_container_width=True)
else:
    st.info("No temple data available for state-wise chart.")

# Temple contributions leaderboard
if not df_contribs.empty and not df_temples.empty:
    contrib_count = df_contribs.groupby("temple_id").size().reset_index(name="Contributions")
    merged = contrib_count.merge(df_temples, left_on="temple_id", right_on="id", how="left")

    fig_leaderboard = px.bar(
        merged.sort_values("Contributions", ascending=False).head(10),
        x="name",
        y="Contributions",
        title="🏆 Top 10 Temples by Contributions",
        color="Contributions",
    )
    st.plotly_chart(fig_leaderboard, use_container_width=True)
else:
    st.info("No contribution data available for temple leaderboard.")
