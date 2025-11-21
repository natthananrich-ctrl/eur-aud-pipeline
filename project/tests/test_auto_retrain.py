"""
test_auto_retrain.py
--------------------
Unit tests สำหรับ AutoRetrain module
"""

import pytest
import pandas as pd
from project.models.auto_retrain import AutoRetrain


@pytest.fixture
def sample_data():
    # ข้อมูลสมมติสำหรับ retrain
    df = pd.DataFrame({
        "feature1": [0.1, 0.2, 0.3, 0.4],
        "feature2": [1, 2, 3, 4],
        "target": [0, 1, 0, 1]
    })
    return df


def test_retrain_trigger(sample_data):
    retrainer = AutoRetrain(env="dev")

    # สมมติ drift ถูกตรวจพบ
    drift_flag = True
    result = retrainer.run(sample_data, drift_flag)

    assert "model_path" in result
    assert "status" in result
    assert result["status"] in ["SUCCESS", "FAIL"]


def test_no_retrain_if_no_drift(sample_data):
    retrainer = AutoRetrain(env="dev")

    # สมมติ drift ไม่ถูกตรวจพบ
    drift_flag = False
    result = retrainer.run(sample_data, drift_flag)

    assert result["status"] == "SKIPPED"


def test_error_handling(sample_data, monkeypatch):
    retrainer = AutoRetrain(env="dev")

    # ทำให้ retrain ล้มเหลว
    def fake_train(*args, **kwargs):
        raise RuntimeError("Training failed")

    monkeypatch.setattr(retrainer, "_train_model", fake_train)

    result = retrainer.run(sample_data, drift_flag=True)
    assert result["status"] == "FAIL"