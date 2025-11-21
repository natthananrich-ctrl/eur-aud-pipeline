{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "437128c5-67b3-44d9-8093-5c4ccd76cdf5",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import json\n",
    "import os\n",
    "from datetime import datetime\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "st.set_page_config(page_title=\"AI Forecast Dashboard\", layout=\"wide\")\n",
    "\n",
    "st.title(\"📊 AI Forecast Monitoring Dashboard\")\n",
    "\n",
    "# Load audit log\n",
    "log_path = \"project/logs/audit.log\"\n",
    "if os.path.exists(log_path):\n",
    "    with open(log_path, \"r\") as f:\n",
    "        logs = [json.loads(line) for line in f.readlines()]\n",
    "    df_log = pd.DataFrame(logs)\n",
    "    df_log[\"timestamp\"] = pd.to_datetime(df_log[\"timestamp\"])\n",
    "else:\n",
    "    st.warning(\"No audit log found.\")\n",
    "    df_log = pd.DataFrame()\n",
    "\n",
    "# Timeline\n",
    "st.subheader(\"📅 Drift & Retrain Timeline\")\n",
    "if not df_log.empty:\n",
    "    drift_events = df_log[df_log[\"message\"].str.contains(\"drift\", case=False)]\n",
    "    st.line_chart(drift_events.set_index(\"timestamp\")[\"module\"].value_counts())\n",
    "else:\n",
    "    st.info(\"No drift/retrain events to show.\")\n",
    "\n",
    "# Performance Summary\n",
    "st.subheader(\"📈 Performance Metrics\")\n",
    "baseline_path = \"project/logs/baseline_metrics.json\"\n",
    "if os.path.exists(baseline_path):\n",
    "    with open(baseline_path, \"r\") as f:\n",
    "        baseline = json.load(f)\n",
    "    st.json(baseline)\n",
    "else:\n",
    "    st.warning(\"No baseline metrics found.\")\n",
    "\n",
    "# Log Viewer\n",
    "st.subheader(\"📁 Audit Log Viewer\")\n",
    "if not df_log.empty:\n",
    "    st.dataframe(df_log.sort_values(\"timestamp\", ascending=False), use_container_width=True)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
