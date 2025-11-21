"""
drift_detector.py
-----------------
โมดูลสำหรับตรวจจับ Performance Drift ของโมเดล
ใช้เปรียบเทียบผลลัพธ์ล่าสุดกับ baseline metrics
"""

import os
import yaml
import json
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error

# โหลด config
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


class DriftDetector:
    def __init__(self, baseline_path="project/logs/baseline_metrics.json"):
        self.config = load_config()
        self.baseline_path = baseline_path
        self.baseline_metrics = self._load_baseline()

    def _load_baseline(self):
        """โหลด baseline metrics จากไฟล์"""
        if os.path.exists(self.baseline_path):
            with open(self.baseline_path, "r") as f:
                return json.load(f)
        else:
            return {"accuracy": None, "f1": None, "rmse": None}

    def save_baseline(self, metrics: dict):
        """บันทึก baseline metrics ใหม่"""
        os.makedirs(os.path.dirname(self.baseline_path), exist_ok=True)
        with open(self.baseline_path, "w") as f:
            json.dump(metrics, f, indent=4)
        print(f"✅ Baseline metrics saved at {self.baseline_path}")

    def detect_drift(self, y_true, y_pred):
        """ตรวจจับ drift โดยเปรียบเทียบกับ baseline"""
        current_metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "rmse": mean_squared_error(y_true, y_pred, squared=False),
        }

        drift_flags = {}
        thresholds = self.config["model"]["retrain_threshold"]

        # ตรวจสอบ drift ของแต่ละ metric
        for metric, baseline_value in self.baseline_metrics.items():
            if baseline_value is None:
                drift_flags[metric] = False
                continue

            diff = abs(current_metrics[metric] - baseline_value)
            drift_flags[metric] = diff > thresholds.get(metric, 0.05)

        drift_detected = any(drift_flags.values())

        return {
            "current_metrics": current_metrics,
            "baseline_metrics": self.baseline_metrics,
            "drift_flags": drift_flags,
            "drift_detected": drift_detected
        }


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # สมมติ baseline metrics
    baseline = {"accuracy": 0.90, "f1": 0.88, "rmse": 0.10}
    detector = DriftDetector()
    detector.save_baseline(baseline)

    # สมมติผลการพยากรณ์ใหม่
    y_true = [0, 1, 0, 1, 0, 1]
    y_pred = [0, 1, 1, 1, 0, 0]

    result = detector.detect_drift(y_true, y_pred)
    print("Drift detection result:", result)