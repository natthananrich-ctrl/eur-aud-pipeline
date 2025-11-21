"""
news_filter.py
--------------
โมดูลสำหรับกรองข่าวเศรษฐกิจที่มีผลกระทบสูง
ใช้ร่วมกับ pipeline เพื่อหลีกเลี่ยงการเข้าเทรดช่วงข่าวแรง
"""

import datetime
import pandas as pd

class NewsFilter:
    def __init__(self, events: pd.DataFrame, symbol: str = "EURAUD", window_minutes: int = 30):
        """
        Parameters
        ----------
        events : pd.DataFrame
            ข้อมูลข่าวที่มีคอลัมน์ ['datetime', 'currency', 'impact', 'event']
        symbol : str
            คู่เงินที่ต้องการกรองข่าว
        window_minutes : int
            ระยะเวลา (นาที) ก่อน/หลังข่าวที่จะถือว่าเป็นช่วงเสี่ยง
        """
        self.events = events.copy()
        self.symbol = symbol
        self.window = datetime.timedelta(minutes=window_minutes)

    def filter_events(self, current_time: datetime.datetime):
        """
        ตรวจสอบว่ามีข่าวแรงที่เกี่ยวข้องกับคู่เงินในช่วงเวลานี้หรือไม่
        """
        risky_events = []
        for _, row in self.events.iterrows():
            event_time = pd.to_datetime(row["datetime"])
            if abs(current_time - event_time) <= self.window:
                if row["impact"].lower() in ["high", "medium"]:
                    if any(cur in self.symbol for cur in row["currency"]):
                        risky_events.append(row.to_dict())

        return risky_events

    def should_trade(self, current_time: datetime.datetime):
        """
        คืนค่า True/False ว่าควรเข้าเทรดหรือไม่
        """
        risky_events = self.filter_events(current_time)
        return len(risky_events) == 0, risky_events


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่าง DataFrame ข่าว
    data = {
        "datetime": [
            "2025-11-20 16:00:00",
            "2025-11-20 16:30:00",
            "2025-11-20 18:00:00",
        ],
        "currency": ["EUR", "AUD", "USD"],
        "impact": ["High", "Medium", "Low"],
        "event": ["ECB Rate Decision", "RBA Statement", "US Housing Data"],
    }
    df_events = pd.DataFrame(data)

    nf = NewsFilter(df_events, symbol="EURAUD", window_minutes=30)

    now = datetime.datetime(2025, 11, 20, 16, 20)
    can_trade, risky = nf.should_trade(now)

    if can_trade:
        print("✅ Safe to trade at", now)
    else:
        print("⚠️ Avoid trading! Risky events:", risky)