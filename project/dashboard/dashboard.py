import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="📊 AI Forecast Dashboard", layout="wide")
st.title("📊 AI Forecast Monitoring Dashboard")

# Load audit log
log_path = "project/logs/audit.log"
if os.path.exists(log_path):
    with open(log_path, "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
    df_log = pd.DataFrame(logs)
    df_log["timestamp"] = pd.to_datetime(df_log["timestamp"])
else:
    st.warning("No audit log found.")
    df_log = pd.DataFrame()

# Load baseline metrics
baseline_path = "project/logs/baseline_metrics.json"
if os.path.exists(baseline_path):
    with open(baseline_path, "r") as f:
        baseline = json.load(f)
else:
    baseline = {}

# Sidebar filter
st.sidebar.header("🔍 Filter Logs")
module_filter = st.sidebar.multiselect("Module", options=df_log["module"].unique())
status_filter = st.sidebar.multiselect("Status", options=df_log["status"].unique())

# Apply filters
filtered_log = df_log.copy()
if module_filter:
    filtered_log = filtered_log[filtered_log["module"].isin(module_filter)]
if status_filter:
    filtered_log = filtered_log[filtered_log["status"].isin(status_filter)]

# Section: Timeline
st.subheader("📅 Drift & Retrain Timeline")
if not df_log.empty:
    drift_events = df_log[df_log["message"].str.contains("drift", case=False)]
    drift_count = drift_events.groupby(drift_events["timestamp"].dt.date)["module"].count()
    st.line_chart(drift_count)
else:
    st.info("No drift/retrain events to show.")

# Section: Performance Summary
st.subheader("📈 Performance Metrics")
if baseline:
    st.json(baseline)
else:
    st.warning("No baseline metrics found.")

# Section: Feature Distribution (optional demo)
st.subheader("📊 Feature Distribution Comparison")
try:
    ref_df = pd.read_csv("project/data/reference.csv")
    new_df = pd.read_csv("project/data/new.csv")
    selected_feature = st.selectbox("Select feature", ref_df.columns)

    fig, ax = plt.subplots()
    sns.kdeplot(ref_df[selected_feature], label="Reference", ax=ax)
    sns.kdeplot(new_df[selected_feature], label="New", ax=ax)
    ax.set_title(f"Distribution of {selected_feature}")
    ax.legend()
    st.pyplot(fig)
except Exception as e:
    st.info("Feature distribution not available. Please check reference.csv and new.csv")

# Section: Log Viewer
st.subheader("📁 Audit Log Viewer")
if not filtered_log.empty:
    st.dataframe(filtered_log.sort_values("timestamp", ascending=False), use_container_width=True)
else:
    st.info("No log entries match the selected filters.")