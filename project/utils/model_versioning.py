"""
model_versioning.py
-------------------
Utility สำหรับบันทึกและโหลดโมเดลพร้อม metadata
"""

import os
import json
import joblib
from datetime import datetime

def save_model_with_metadata(model, metrics, drift_result=None, env="prod", version=None):
    """
    บันทึกโมเดลพร้อม metadata ลงใน project/models/versions/{env}/
    """
    version_dir = f"project/models/versions/{env}/"
    os.makedirs(version_dir, exist_ok=True)

    # ตั้งชื่อเวอร์ชันอัตโนมัติถ้าไม่กำหนดเอง
    if version is None:
        version = datetime.now().strftime("%Y%m%d_%H%M%S")

    model_path = os.path.join(version_dir, f"model_{version}.pkl")
    meta_path = os.path.join(version_dir, f"model_{version}.json")

    # บันทึกโมเดล
    joblib.dump(model, model_path)

    # บันทึก metadata
    metadata = {
        "version": version,
        "env": env,
        "train_date": datetime.now().isoformat(),
        "metrics": metrics,
        "drift_result": drift_result
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)

    return model_path, meta_path


def load_model_with_metadata(env="prod", version=None):
    """
    โหลดโมเดลและ metadata จาก project/models/versions/{env}/
    ถ้าไม่กำหนด version จะโหลดเวอร์ชันล่าสุด
    """
    version_dir = f"project/models/versions/{env}/"

    if not os.path.exists(version_dir):
        raise FileNotFoundError(f"No versions found for env={env}")

    if version is None:
        # หาไฟล์ล่าสุด
        files = sorted([f for f in os.listdir(version_dir) if f.endswith(".pkl")])
        if not files:
            raise FileNotFoundError("No model versions found.")
        latest_model = files[-1]
        version = latest_model.replace("model_", "").replace(".pkl", "")

    model_path = os.path.join(version_dir, f"model_{version}.pkl")
    meta_path = os.path.join(version_dir, f"model_{version}.json")

    model = joblib.load(model_path)
    with open(meta_path, "r") as f:
        metadata = json.load(f)

    return model, metadata