"""
run_pipeline.py
---------------
Pipeline พร้อม Error Handling + AuditLogger
"""

import pandas as pd
from project.utils.logger import AuditLogger
from project.utils.config_loader import load_config
from project.features.feature_generator import FeatureGenerator
from project.models.model_selector import ModelSelector
from project.models.drift_detector import DriftDetector

def run_pipeline(env="dev"):
    logger = AuditLogger()

    try:
        # 1. โหลด config
        config = load_config(env=env)

        # 2. โหลดข้อมูล
        try:
            df = pd.read_csv(config["data"]["source_path"])
            logger.log_event("pipeline", "load_data", "SUCCESS", f"rows={len(df)}")
        except Exception as e:
            logger.log_event("pipeline", "load_data", "FAIL", str(e))
            # fallback → ใช้ dataset ว่างเพื่อไม่ให้ pipeline ล้ม
            df = pd.DataFrame()
        
        # 3. สร้าง features
        try:
            fg = FeatureGenerator(df)
            df_features = fg.generate_all_features()
            logger.log_event("features", "generate_all_features", "SUCCESS", "Features generated")
        except Exception as e:
            logger.log_event("features", "generate_all_features", "FAIL", str(e))
            # fallback → ใช้ features ว่าง
            df_features = pd.DataFrame()

        # 4. Train models
        try:
            selector = ModelSelector(df_features, criterion=config["model"]["criterion"])
            best_model, metrics = selector.select_best_model()
            logger.log_event("models", "model_selector", "SUCCESS", f"best_model={best_model}, metrics={metrics}")
        except Exception as e:
            logger.log_event("models", "model_selector", "FAIL", str(e))
            best_model, metrics = None, {}

        # 5. Drift detection
        try:
            detector = DriftDetector(df_features)
            drift_result = detector.check_drift()
            logger.log_event("models", "drift_detector", "SUCCESS", f"drift_detected={drift_result}")
        except Exception as e:
            logger.log_event("models", "drift_detector", "FAIL", str(e))
            drift_result = None

        logger.log_event("pipeline", "run_pipeline", "SUCCESS", "Pipeline completed with error handling")
        print("✅ Pipeline finished (with error handling).")

        return {"best_model": best_model, "metrics": metrics, "drift": drift_result}

    except Exception as e:
        logger.log_event("pipeline", "run_pipeline", "FAIL", str(e))
        raise


if __name__ == "__main__":
    run_pipeline(env="dev")