"""
test_features.py
----------------
Unit tests สำหรับโมดูลฟีเจอร์
"""

import pytest
import pandas as pd
from project.features.feature_generator import FeatureGenerator
from project.features.fibo_levels import FiboLevels
from project.features.volume_features import VolumeFeatures


@pytest.fixture
def sample_data():
    data = {
        "datetime": pd.date_range("2025-11-01", periods=10, freq="D"),
        "open": [1.60, 1.61, 1.62, 1.58, 1.57, 1.59, 1.63, 1.62, 1.64, 1.65],
        "high": [1.61, 1.62, 1.63, 1.59, 1.58, 1.60, 1.64, 1.63, 1.65, 1.66],
        "low":  [1.59, 1.60, 1.61, 1.57, 1.56, 1.58, 1.62, 1.61, 1.63, 1.64],
        "close":[1.60, 1.61, 1.62, 1.58, 1.57, 1.59, 1.63, 1.62, 1.64, 1.65],
        "volume":[100, 120, 130, 90, 80, 110, 150, 140, 160, 170]
    }
    return pd.DataFrame(data)


def test_feature_generator(sample_data):
    fg = FeatureGenerator(sample_data)
    df = fg.generate_all_features()

    # ตรวจสอบว่ามี RSI และ MACD
    assert "RSI" in df.columns
    assert "MACD" in df.columns

    # RSI ต้องอยู่ในช่วง 0–100
    assert df["RSI"].between(0, 100).all()


def test_fibo_levels(sample_data):
    fibo = FiboLevels()
    df = fibo.generate_levels_for_dataframe(sample_data, lookback=5)

    # ต้องมีคอลัมน์ fibo_high และ fibo_low
    assert "fibo_high" in df.columns
    assert "fibo_low" in df.columns

    # fibo_high ต้อง >= fibo_low
    assert (df["fibo_high"] >= df["fibo_low"]).all()


def test_volume_features(sample_data):
    vf = VolumeFeatures(sample_data)
    df = vf.generate_all_volume_features()

    # ต้องมีคอลัมน์ volume_ma และ volume_ratio
    assert "volume_ma" in df.columns
    assert "volume_ratio" in df.columns

    # volume_ratio ต้องไม่เป็น NaN ทั้งหมด
    assert df["volume_ratio"].notna().any()