"""
drift_detector.py
-----------------
Hybrid Drift Detector:
- ตรวจ Performance Drift (accuracy, f1, rmse)
- ตรวจ Data Drift (distribution ของ features)
"""

import os
import json
import pandas as pd
import yaml
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
from scipy.stats import ks_2samp
from project.utils.logger import AuditLogger
from project.utils.config_loader import load_config


class DriftDetector:
    def __init__(self, env="dev", baseline_path="project/logs/baseline_metrics.json"):
        self.config = load_config(env)
        self.logger = AuditLogger()
        self.baseline_path = baseline_path
        self.baseline_metrics = self._load_baseline()
        self.perf_thresholds = self.config["model"].get("retrain_threshold", {})
        self.data_threshold = self.config["drift"].get("p_value_threshold", 0.05)

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
        self.logger.log("drift_detector", "Baseline metrics updated", "SUCCESS")

    def detect_performance_drift(self, y_true, y_pred):
        """ตรวจ Performance Drift"""
        current_metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "rmse": mean_squared_error(y_true, y_pred, squared=False),
        }

        drift_flags = {}
        for metric, baseline_value in self.baseline_metrics.items():
            if baseline_value is None:
                drift_flags[metric] = False
                continue
            diff = abs(current_metrics[metric] - baseline_value)
            drift_flags[metric] = diff > self.perf_thresholds.get(metric, 0.05)

        drift_detected = any(drift_flags.values())
        self.logger.log("drift_detector", f"Performance drift={drift_detected}", "SUCCESS")

        return {
            "current_metrics": current_metrics,
            "baseline_metrics": self.baseline_metrics,
            "drift_flags": drift_flags,
            "drift_detected": drift_detected
        }

    def detect_data_drift(self, reference_df: pd.DataFrame, new_df: pd.DataFrame):
        """ตรวจ Data Drift"""
        if reference_df.empty or new_df.empty:
            self.logger.log("drift_detector", "Empty dataframes", "FAIL")
            return {"overall_drift": False, "details": {}}

        drift_results = {}
        drift_detected = False

        for col in reference_df.columns:
            if col not in new_df.columns:
                self.logger.log("drift_detector", f"Missing column {col}", "FAIL")
                continue

            try:
                stat, p_value = ks_2samp(reference_df[col], new_df[col])
                drift_results[col] = {"p_value": p_value, "drift_detected": p_value < self.data_threshold}
                if p_value < self.data_threshold:
                    drift_detected = True
            except Exception as e:
                self.logger.log("drift_detector", f"Error on {col}: {e}", "FAIL")
                drift_results[col] = {"p_value": None, "drift_detected": None}

        self.logger.log("drift_detector", f"Data drift={drift_detected}", "SUCCESS")
        return {"overall_drift": drift_detected, "details": drift_results}