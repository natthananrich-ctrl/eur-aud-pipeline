"""
auto_retrain.py
---------------
โมดูลสำหรับ retrain โมเดลอัตโนมัติเมื่อพบ drift
เชื่อมกับ DriftDetector และ ModelTrainer
"""

import os
import yaml
import pandas as pd
from project.models.drift_detector import DriftDetector
from project.models.train_model import ModelTrainer

# โหลด config
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


class AutoRetrain:
    def __init__(self, df: pd.DataFrame, target_col: str = "direction"):
        self.df = df.copy()
        self.target_col = target_col
        self.config = load_config()
        self.detector = DriftDetector()

    def check_and_retrain(self, y_true, y_pred):
        """
        ตรวจ drift และ retrain ถ้าจำเป็น
        """
        result = self.detector.detect_drift(y_true, y_pred)

        if result["drift_detected"]:
            print("⚠️ Drift detected! Starting retrain process...")
            trainer = ModelTrainer(self.df, target_col=self.target_col)
            X_train, X_test, y_train, y_test = trainer.prepare_data()

            # retrain XGBoost เป็น default
            model, metrics = trainer.train_xgboost(X_train, y_train, X_test, y_test)
            trainer.save_model(model, "xgboost_retrained")

            # update baseline
            self.detector.save_baseline(metrics)
            print("✅ Retrain completed and baseline updated.")
            return model, metrics
        else:
            print("✅ No drift detected. Model is stable.")
            return None, result["current_metrics"]


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

    auto = AutoRetrain(df, target_col="direction")

    # สมมติผลการพยากรณ์ใหม่
    y_true = [0, 1, 0, 1, 0]
    y_pred = [0, 1, 1, 1, 0]

    model, metrics = auto.check_and_retrain(y_true, y_pred)
    print("Result metrics:", metrics)