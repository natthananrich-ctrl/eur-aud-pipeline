"""
model_selector.py
-----------------
โมดูลสำหรับเลือกโมเดลที่ดีที่สุดจากผลการฝึก
รองรับการทำ Ensemble ด้วย Weighted Voting
"""

import os
import yaml
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error

# โหลด config และ hyperparameters
def load_config():
    with open("project/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    with open("project/config/model_params.yaml", "r") as f:
        params = yaml.safe_load(f)
    return config, params


class ModelSelector:
    def __init__(self, models: dict, metrics: dict):
        """
        Parameters
        ----------
        models : dict
            {"xgboost": model_obj, "lightgbm": model_obj, "lstm": model_obj}
        metrics : dict
            {"xgboost": {"accuracy": ..., "f1": ..., "rmse": ...}, ...}
        """
        self.models = models
        self.metrics = metrics
        self.config, self.params = load_config()

    def select_best_model(self, criterion: str = "accuracy"):
        """
        เลือกโมเดลที่ดีที่สุดตาม criterion
        """
        best_model = None
        best_score = -np.inf
        best_name = None

        for name, m in self.metrics.items():
            score = m.get(criterion, None)
            if score is not None and score > best_score:
                best_score = score
                best_model = self.models[name]
                best_name = name

        print(f"✅ Best model selected: {best_name} ({criterion}={best_score:.4f})")
        return best_name, best_model

    def ensemble_predict(self, X):
        """
        ทำ Ensemble ด้วย Weighted Voting
        """
        weights = self.params["ensemble"]["weights"]
        preds = []

        for name, model in self.models.items():
            if name == "lstm":
                # reshape สำหรับ LSTM
                X_input = np.expand_dims(X, axis=1)
                pred = (model.predict(X_input) > 0.5).astype(int).flatten()
            else:
                pred = model.predict(X)
            preds.append(weights[name] * pred)

        final_pred = np.round(np.sum(preds, axis=0) / sum(weights.values())).astype(int)
        return final_pred

    def evaluate_ensemble(self, X, y_true):
        """
        ประเมินผล Ensemble
        """
        y_pred = self.ensemble_predict(X)
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "rmse": mean_squared_error(y_true, y_pred, squared=False)
        }

    def save_best_model(self, model, name: str):
        """บันทึกโมเดลที่เลือก"""
        path = os.path.join(self.config["pipeline"]["outputs_path"], f"{name}_best.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        print(f"✅ Best model saved at {path}")


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # สมมติว่ามีโมเดลและ metrics ที่ได้จาก train_model.py
    dummy_models = {"xgboost": None, "lightgbm": None, "lstm": None}
    dummy_metrics = {
        "xgboost": {"accuracy": 0.85, "f1": 0.83, "rmse": 0.12},
        "lightgbm": {"accuracy": 0.87, "f1": 0.85, "rmse": 0.11},
        "lstm": {"accuracy": 0.82, "f1": 0.80, "rmse": 0.15},
    }

    selector = ModelSelector(dummy_models, dummy_metrics)
    best_name, best_model = selector.select_best_model(criterion="accuracy")
    print("Best model:", best_name)