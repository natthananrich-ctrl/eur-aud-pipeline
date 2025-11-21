"""
fibo_predictor.py
-----------------
โมดูลสำหรับใช้สัญญาณ Fibonacci + ฟีเจอร์อื่น ๆ
เพื่อทำนายโอกาสขึ้น/ลงของราคา EURAUD
"""

import os
import yaml
import joblib
import pandas as pd
import numpy as np

# โหลด config
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


class FiboPredictor:
    def __init__(self, model_path="project/outputs/xgboost_model.pkl"):
        """
        Parameters
        ----------
        model_path : str
            path ของโมเดลที่ฝึกไว้
        """
        self.config = load_config()
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        """โหลดโมเดลจากไฟล์"""
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        else:
            raise FileNotFoundError(f"❌ Model not found at {self.model_path}")

    def prepare_features(self, df: pd.DataFrame):
        """
        เตรียมฟีเจอร์สำหรับการพยากรณ์
        - แปลง fibo_signal เป็น one-hot
        - รวมกับ indicators และ volume features
        """
        df = df.copy()

        # One-hot encoding ของ fibo_signal
        fibo_dummies = pd.get_dummies(df["fibo_signal"], prefix="fibo")
        df = pd.concat([df, fibo_dummies], axis=1)

        # ลบคอลัมน์ที่ไม่ใช่ฟีเจอร์
        drop_cols = ["fibo_levels", "fibo_signal"]
        for col in drop_cols:
            if col in df.columns:
                df = df.drop(columns=[col])

        return df

    def predict(self, df: pd.DataFrame):
        """
        ทำนายโอกาสขึ้น/ลงจากฟีเจอร์
        Returns
        -------
        pd.DataFrame
            DataFrame ที่มี prediction และ probability
        """
        features = self.prepare_features(df)
        preds = self.model.predict(features)
        probs = self.model.predict_proba(features)[:, 1]

        df["prediction"] = preds
        df["probability_up"] = probs
        df["probability_down"] = 1 - probs
        return df


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่าง DataFrame
    data = {
        "close": [1.635, 1.638, 1.639],
        "fibo_signal": ["retracement_0.382", "none", "extension_1.618"],
        "rsi": [45, 55, 62],
        "macd": [0.01, 0.02, -0.01],
        "volume": [1000, 1200, 900],
    }
    df = pd.DataFrame(data)

    predictor = FiboPredictor(model_path="project/outputs/xgboost_model.pkl")
    df_pred = predictor.predict(df)
    print(df_pred[["close", "prediction", "probability_up", "probability_down"]])