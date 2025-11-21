"""
train_model.py
--------------
โมดูลสำหรับฝึกโมเดลพยากรณ์ราคา Forex
รองรับ XGBoost, LightGBM และ LSTM
"""

import os
import yaml
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
import joblib

# ML libraries
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# โหลด config และ hyperparameters
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    with open("project/config/model_params.yaml", "r") as f:
        params = yaml.safe_load(f)
    return config, params


class ModelTrainer:
    def __init__(self, df: pd.DataFrame, target_col: str = "direction"):
        self.df = df.copy()
        self.target_col = target_col
        self.config, self.params = load_config()

    def prepare_data(self):
        """เตรียมข้อมูลสำหรับโมเดล"""
        X = self.df.drop(columns=[self.target_col])
        y = self.df[self.target_col]
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """ฝึกโมเดล XGBoost"""
        model = xgb.XGBClassifier(**self.params["xgboost"])
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = self.evaluate(y_test, preds)
        return model, metrics

    def train_lightgbm(self, X_train, y_train, X_test, y_test):
        """ฝึกโมเดล LightGBM"""
        model = lgb.LGBMClassifier(**self.params["lightgbm"])
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = self.evaluate(y_test, preds)
        return model, metrics

    def train_lstm(self, X_train, y_train, X_test, y_test):
        """ฝึกโมเดล LSTM"""
        input_dim = X_train.shape[1]
        model = Sequential()
        model.add(LSTM(self.params["lstm"]["hidden_units"], input_shape=(1, input_dim), return_sequences=False))
        model.add(Dropout(self.params["lstm"]["dropout"]))
        model.add(Dense(1, activation="sigmoid"))

        optimizer = Adam(learning_rate=self.params["lstm"]["learning_rate"])
        model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])

        # reshape สำหรับ LSTM (samples, timesteps, features)
        X_train_lstm = np.expand_dims(X_train, axis=1)
        X_test_lstm = np.expand_dims(X_test, axis=1)

        model.fit(X_train_lstm, y_train, epochs=self.params["lstm"]["epochs"], batch_size=self.params["lstm"]["batch_size"], verbose=0)
        preds = (model.predict(X_test_lstm) > 0.5).astype(int).flatten()
        metrics = self.evaluate(y_test, preds)
        return model, metrics

    def evaluate(self, y_true, y_pred):
        """คำนวณ metrics"""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "rmse": mean_squared_error(y_true, y_pred, squared=False)
        }

    def save_model(self, model, name: str):
        """บันทึกโมเดล"""
        path = os.path.join(self.config["pipeline"]["outputs_path"], f"{name}.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        print(f"✅ Model saved at {path}")


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่าง DataFrame
    data = {
        "feature1": [0.1, 0.2, 0.3, 0.4, 0.5],
        "feature2": [1, 2, 3, 4, 5],
        "direction": [0, 1, 0, 1, 0],
    }
    df = pd.DataFrame(data)

    trainer = ModelTrainer(df, target_col="direction")
    X_train, X_test, y_train, y_test = trainer.prepare_data()

    # Train XGBoost
    model, metrics = trainer.train_xgboost(X_train, y_train, X_test, y_test)
    print("XGBoost metrics:", metrics)
    trainer.save_model(model, "xgboost_model")