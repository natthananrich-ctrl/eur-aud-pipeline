"""
backtest.py
-----------
Backtest engine พร้อม AuditLogger + Config Management
"""

import pandas as pd
from project.utils.logger import AuditLogger
from project.backtest.backtester import Backtester   # สมมติว่ามี Backtester class
from project.utils.config_loader import load_config  # ฟังก์ชันโหลด config

def run_backtest(env="test"):
    logger = AuditLogger()

    try:
        # 1. โหลด config ตาม environment
        config = load_config(env=env)
        data_path = config["data"]["source_path"]
        initial_balance = config["backtest"]["initial_balance"]

        # 2. โหลดข้อมูลราคา
        df = pd.read_csv(data_path)
        logger.log_event("backtest", "load_data", "SUCCESS", f"rows={len(df)}")

        # 3. รัน backtest
        bt = Backtester(df, initial_balance=initial_balance)
        results = bt.run()
        logger.log_event("backtest", "run", "SUCCESS",
                         f"trades={results['trades']}, win_rate={results['win_rate']:.2f}, "
                         f"final_balance={results['final_balance']:.2f}")

        # 4. บันทึกผลลัพธ์เพิ่มเติม เช่น equity curve
        if "equity_curve" in results:
            logger.log_event("backtest", "equity_curve", "SUCCESS",
                             f"points={len(results['equity_curve'])}")

        print("✅ Backtest completed successfully.")
        return results

    except Exception as e:
        logger.log_event("backtest", "run_backtest", "FAIL", str(e))
        raise


if __name__ == "__main__":
    # เลือก environment ได้: dev / test / prod
    run_backtest(env="test")