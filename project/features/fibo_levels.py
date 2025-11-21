"""
fibo_levels.py
--------------
โมดูลสำหรับคำนวณ Fibonacci retracement และ extension levels
ใช้สำหรับวิเคราะห์แนวรับ/แนวต้าน และจุดกลับตัวของราคา
"""

import pandas as pd

class FiboLevels:
    def __init__(self, retracements=None, extensions=None):
        """
        Parameters
        ----------
        retracements : list
            ค่า retracement เช่น [0.236, 0.382, 0.5, 0.618, 0.786]
        extensions : list
            ค่า extension เช่น [1.272, 1.618, 2.0]
        """
        self.retracements = retracements or [0.236, 0.382, 0.5, 0.618, 0.786]
        self.extensions = extensions or [1.272, 1.618, 2.0]

    def calculate_levels(self, swing_high: float, swing_low: float):
        """
        คำนวณ Fibonacci retracement และ extension จาก swing high/low

        Parameters
        ----------
        swing_high : float
            จุดสูงสุดของราคา
        swing_low : float
            จุดต่ำสุดของราคา

        Returns
        -------
        dict
            levels = {
                "retracements": {0.236: value, 0.382: value, ...},
                "extensions": {1.272: value, 1.618: value, ...}
            }
        """
        diff = swing_high - swing_low
        retracement_levels = {r: swing_high - diff * r for r in self.retracements}
        extension_levels = {e: swing_high + diff * (e - 1) for e in self.extensions}

        return {
            "retracements": retracement_levels,
            "extensions": extension_levels
        }

    def generate_levels_for_dataframe(self, df: pd.DataFrame, lookback=50):
        """
        สร้าง Fibonacci levels สำหรับ DataFrame โดยใช้ rolling window

        Parameters
        ----------
        df : pd.DataFrame
            ข้อมูลราคา Forex ที่มีคอลัมน์ ['high', 'low', 'close']
        lookback : int
            จำนวนแท่งย้อนหลังที่ใช้หาจุด swing high/low

        Returns
        -------
        pd.DataFrame
            DataFrame ที่มีคอลัมน์ retracement และ extension levels
        """
        fibo_data = []
        for i in range(len(df)):
            if i < lookback:
                fibo_data.append({})
                continue

            swing_high = df["high"].iloc[i-lookback:i].max()
            swing_low = df["low"].iloc[i-lookback:i].min()
            levels = self.calculate_levels(swing_high, swing_low)
            fibo_data.append(levels)

        df["fibo_levels"] = fibo_data
        return df


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    data = {
        "high": [1.64, 1.645, 1.642, 1.650, 1.655],
        "low": [1.62, 1.63, 1.632, 1.635, 1.640],
        "close": [1.635, 1.638, 1.639, 1.642, 1.648],
    }
    df = pd.DataFrame(data)

    fibo = FiboLevels()
    df = fibo.generate_levels_for_dataframe(df, lookback=3)

    print(df[["high", "low", "fibo_levels"]])