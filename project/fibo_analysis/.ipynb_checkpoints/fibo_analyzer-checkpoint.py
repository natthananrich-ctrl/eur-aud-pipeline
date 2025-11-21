"""
fibo_analyzer.py
----------------
โมดูลสำหรับวิเคราะห์พฤติกรรมราคาที่สัมพันธ์กับ Fibonacci levels
ตรวจสอบการแตะระดับ retracement/extension และสร้างสัญญาณ
"""

import pandas as pd

class FiboAnalyzer:
    def __init__(self, df: pd.DataFrame, fibo_col: str = "fibo_levels", tolerance: float = 0.0005):
        """
        Parameters
        ----------
        df : pd.DataFrame
            ข้อมูลราคา Forex ที่มีคอลัมน์ ['close', 'fibo_levels']
        fibo_col : str
            คอลัมน์ที่เก็บค่า Fibonacci levels (dict retracements/extensions)
        tolerance : float
            ระยะห่างที่ถือว่า "แตะ" ระดับ Fibonacci (เช่น 0.0005 ~ 5 pips)
        """
        self.df = df.copy()
        self.fibo_col = fibo_col
        self.tolerance = tolerance

    def check_touch_levels(self):
        """
        ตรวจสอบว่าราคา close แตะหรือใกล้ Fibonacci levels
        """
        signals = []
        for idx, row in self.df.iterrows():
            fibo_data = row[self.fibo_col]
            if not fibo_data or not isinstance(fibo_data, dict):
                signals.append("none")
                continue

            close_price = row["close"]
            touched = []

            # ตรวจ retracements
            for level, value in fibo_data.get("retracements", {}).items():
                if abs(close_price - value) <= self.tolerance:
                    touched.append(f"retracement_{level}")

            # ตรวจ extensions
            for level, value in fibo_data.get("extensions", {}).items():
                if abs(close_price - value) <= self.tolerance:
                    touched.append(f"extension_{level}")

            signals.append(",".join(touched) if touched else "none")

        self.df["fibo_signal"] = signals
        return self.df

    def generate_summary(self):
        """
        สรุปจำนวนครั้งที่แตะ Fibonacci levels
        """
        summary = self.df["fibo_signal"].value_counts().to_dict()
        return summary


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่าง DataFrame
    data = {
        "close": [1.635, 1.638, 1.639, 1.642, 1.648],
        "fibo_levels": [
            {"retracements": {0.382: 1.636}, "extensions": {1.618: 1.645}},
            {"retracements": {0.382: 1.638}, "extensions": {1.618: 1.646}},
            {"retracements": {0.382: 1.640}, "extensions": {1.618: 1.648}},
            {"retracements": {0.382: 1.642}, "extensions": {1.618: 1.650}},
            {"retracements": {0.382: 1.648}, "extensions": {1.618: 1.655}},
        ],
    }
    df = pd.DataFrame(data)

    analyzer = FiboAnalyzer(df, tolerance=0.001)
    df = analyzer.check_touch_levels()
    print(df[["close", "fibo_signal"]])

    summary = analyzer.generate_summary()
    print("Summary:", summary)