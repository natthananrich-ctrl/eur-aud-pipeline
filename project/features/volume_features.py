"""
volume_features.py
------------------
โมดูลสำหรับสร้างฟีเจอร์จาก Volume
เช่น Volume Spike, Moving Average, Divergence
"""

import pandas as pd
import numpy as np

class VolumeFeatures:
    def __init__(self, df: pd.DataFrame):
        """
        Parameters
        ----------
        df : pd.DataFrame
            ข้อมูลราคา Forex ที่มีคอลัมน์ ['open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()

    def add_volume_ma(self, window: int = 20):
        """เพิ่มค่า Moving Average ของ Volume"""
        self.df[f"volume_ma_{window}"] = self.df["volume"].rolling(window=window).mean()
        return self.df

    def add_volume_spike(self, threshold: float = 1.5, window: int = 20):
        """
        ตรวจจับ Volume Spike เมื่อ volume > threshold * volume_ma
        Parameters
        ----------
        threshold : float
            ค่าที่ใช้กำหนดว่า volume สูงผิดปกติ (เช่น 1.5 เท่าของค่าเฉลี่ย)
        window : int
            จำนวนแท่งย้อนหลังที่ใช้คำนวณค่าเฉลี่ย
        """
        ma = self.df["volume"].rolling(window=window).mean()
        self.df["volume_spike"] = (self.df["volume"] > threshold * ma).astype(int)
        return self.df

    def add_volume_divergence(self, price_col: str = "close", window: int = 20):
        """
        ตรวจจับ Divergence ระหว่างราคาและ Volume
        - ถ้าราคาเพิ่มขึ้น แต่ Volume ลดลง → bearish divergence
        - ถ้าราคาลดลง แต่ Volume เพิ่มขึ้น → bullish divergence
        """
        price_change = self.df[price_col].pct_change(window)
        volume_change = self.df["volume"].pct_change(window)

        conditions = []
        for p, v in zip(price_change, volume_change):
            if p > 0 and v < 0:
                conditions.append("bearish_divergence")
            elif p < 0 and v > 0:
                conditions.append("bullish_divergence")
            else:
                conditions.append("none")

        self.df["volume_divergence"] = conditions
        return self.df

    def generate_all_volume_features(self):
        """รวมทุกฟีเจอร์ Volume"""
        self.add_volume_ma()
        self.add_volume_spike()
        self.add_volume_divergence()
        return self.df


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    data = {
        "open": [1.63, 1.64, 1.635, 1.638, 1.640],
        "high": [1.64, 1.645, 1.64, 1.642, 1.646],
        "low": [1.62, 1.63, 1.632, 1.635, 1.638],
        "close": [1.635, 1.638, 1.639, 1.640, 1.642],
        "volume": [1000, 1200, 1100, 1300, 900],
    }
    df = pd.DataFrame(data)

    vf = VolumeFeatures(df)
    df_features = vf.generate_all_volume_features()
    print(df_features[["close", "volume", "volume_ma_20", "volume_spike", "volume_divergence"]])