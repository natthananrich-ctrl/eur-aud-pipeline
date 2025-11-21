"""
test_models.py
--------------
Unit tests สำหรับโมดูลโมเดล
"""

import pytest
import pandas as pd
import numpy as np
from project.models.train_model import ModelTrainer
from project.models.model_selector import ModelSelector
from project.models.drift_detector import DriftDetector


@pytest.fixture
def sample_data():
    # สร้างข้อมูลจำลองสำหรับทดสอบ
    np.random.seed(42)
    data = {
        "feature1": np.random.randn(100),
        "feature2": np.random.randn(100),
        "direction": np.random.choice([0, 1], size=100)
    }
    return pd.DataFrame(data)


def test_model_trainer(sample_data):
    trainer = ModelTrainer(sample_data, target_col="direction")
    X_train, X_test, y_train, y_test = trainer.prepare_data()

    # ตรวจสอบว่า split ถูกต้อง
    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(y_train) > 0
    assert len(y_test) > 0

    # Train XGBoost
    model, metrics = trainer.train_xgboost(X_train, y_train, X_test, y_test)
    assert "accuracy" in metrics
    assert metrics["accuracy"] >= 0  # accuracy ต้อง >= 0


def test_model_selector(sample_data):
    trainer = ModelTrainer(sample_data, target_col="direction")
    X_train, X_test, y_train, y_test = trainer.prepare_data()

    models = {}
    metrics = {}

    models["xgboost"], metrics["xgboost"] = trainer.train_xgboost(X_train, y_train, X_test, y_test)
    models["lightgbm"], metrics["lightgbm"] = trainer.train_lightgbm(X_train, y_train, X_test, y_test)

    selector = ModelSelector(models, metrics)
    best_name, best_model = selector.select_best_model(criterion="accuracy")

    # ต้องเลือกโมเดลที่มีชื่ออยู่ใน dict
    assert best_name in models
    assert best_model is not None


def test_drift_detector(sample_data):
    trainer = ModelTrainer(sample_data, target_col="direction")
    X_train, X_test, y_train, y_test = trainer.prepare_data()

    model, metrics = trainer.train_xgboost(X_train, y_train, X_test, y_test)
    y_pred = model.predict(X_test)

    detector = DriftDetector()
    drift_result = detector.detect_drift(y_test, y_pred)

    # ต้องคืนค่าเป็น dict และมี key 'drift_detected'
    assert isinstance(drift_result, dict)
    assert "drift_detected" in drift_result