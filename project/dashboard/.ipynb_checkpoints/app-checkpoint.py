"""
app.py
------
Flask Dashboard สำหรับดูผลพยากรณ์และกราฟแบบ Real-Time
"""

import os
import yaml
import pandas as pd
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.io as pio

from project.prediction.live_predictor import LivePredictor

# โหลด config
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


app = Flask(__name__)
config = load_config()
live_predictor = LivePredictor(model_path="project/outputs/xgboost_model.pkl")


@app.route("/")
def index():
    """หน้าแรก"""
    return render_template("index.html")


@app.route("/api/predict")
def api_predict():
    """API สำหรับดึงสัญญาณล่าสุด"""
    df_live = live_predictor.fetch_live_data(bars=300)
    df_features = live_predictor.generate_features(df_live)
    latest = live_predictor.predict_live(df_features)

    return jsonify({
        "datetime": str(latest["datetime"]),
        "close": float(latest["close"]),
        "signal": "BUY" if latest["prediction"] == 1 else "SELL",
        "prob_up": float(latest["probability_up"]),
        "prob_down": float(latest["probability_down"])
    })


@app.route("/chart")
def chart():
    """แสดงกราฟราคาพร้อมสัญญาณ"""
    df_live = live_predictor.fetch_live_data(bars=300)
    df_features = live_predictor.generate_features(df_live)
    df_pred = live_predictor.predict_live(df_features)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_features["datetime"],
        open=df_features["open"],
        high=df_features["high"],
        low=df_features["low"],
        close=df_features["close"],
        name="Price"
    ))

    # เพิ่มสัญญาณ BUY/SELL
    signals = df_features.copy()
    signals["signal"] = df_pred["prediction"]

    buy_points = signals[signals["signal"] == 1]
    sell_points = signals[signals["signal"] == 0]

    fig.add_trace(go.Scatter(
        x=buy_points["datetime"], y=buy_points["close"],
        mode="markers", marker=dict(color="green", size=10),
        name="BUY"
    ))

    fig.add_trace(go.Scatter(
        x=sell_points["datetime"], y=sell_points["close"],
        mode="markers", marker=dict(color="red", size=10),
        name="SELL"
    ))

    fig.update_layout(title="EURAUD Live Prediction", xaxis_rangeslider_visible=False)

    graph_html = pio.to_html(fig, full_html=False)
    return render_template("chart.html", graph_html=graph_html)


# ============================
# Run Flask App
# ============================
if __name__ == "__main__":
    app.run(host=config["dashboard"]["host"], port=config["dashboard"]["port"], debug=True)