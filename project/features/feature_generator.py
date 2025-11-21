"""
feature_generator.py
--------------------
โมดูลสำหรับสร้างฟีเจอร์จากข้อมูลราคา Forex (OHLCV)
รวม Indicators, Candle Patterns, และสถิติพื้นฐาน
"""

import pandas as pd
import numpy as np
import ta  # technical analysis library (pip install ta)

class FeatureGenerator:
    def __init__(self, df: pd.DataFrame):
        """
        Parameters
        ----------
        df : pd.DataFrame
            ข้อมูลราคา Forex ที่มีคอลัมน์ ['open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()

    def add_basic_features(self):
        """เพิ่มฟีเจอร์พื้นฐาน เช่น return, volatility"""
        self.df["return"] = self.df["close"].pct_change()
        self.df["log_return"] = np.log(self.df["close"] / self.df["close"].shift(1))
        self.df["volatility"] = self.df["return"].rolling(window=20).std()
        return self.df

    def add_indicators(self):
        """เพิ่ม Indicators เช่น RSI, MACD, ATR, Bollinger Bands"""
        # RSI
        self.df["rsi"] = ta.momentum.RSIIndicator(self.df["close"], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(self.df["close"])
        self.df["macd"] = macd.macd()
        self.df["macd_signal"] = macd.macd_signal()
        self.df["macd_diff"] = macd.macd_diff()

        # ATR
        atr = ta.volatility.AverageTrueRange(
            high=self.df["high"], low=self.df["low"], close=self.df["close"], window=14
        )
        self.df["atr"] = atr.average_true_range()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(self.df["close"], window=20, window_dev=2)
        self.df["bb_high"] = bb.bollinger_hband()
        self.df["bb_low"] = bb.bollinger_lband()
        self.df["bb_width"] = self.df["bb_high"] - self.df["bb_low"]

        return self.df

    def add_candle_patterns(self):
        """เพิ่มฟีเจอร์จาก Candle เช่น body size, upper/lower shadow"""
        self.df["candle_body"] = self.df["close"] - self.df["open"]
        self.df["candle_range"] = self.df["high"] - self.df["low"]
        self.df["upper_shadow"] = self.df["high"] - self.df[["close", "open"]].max(axis=1)
        self.df["lower_shadow"] = self.df[["close", "open"]].min(axis=1) - self.df["low"]

        # ตัวอย่าง pattern: bullish engulfing
        self.df["bullish_engulfing"] = (
            (self.df["candle_body"] > 0) &
            (self.df["candle_body"].shift(1) < 0) &
            (self.df["close"] > self.df["open"].shift(1)) &
            (self.df["open"] < self.df["close"].shift(1))
        ).astype(int)

        return self.df

    def generate_all_features(self):
        """รวมทุกฟีเจอร์เข้าด้วยกัน"""
        self.add_basic_features()
        self.add_indicators()
        self.add_candle_patterns()
        return self.df


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่าง DataFrame
    data = {
        "open": [1.63, 1.64, 1.635, 1.638],
        "high": [1.64, 1.645, 1.64, 1.642],
        "low": [1.62, 1.63, 1.632, 1.635],
        "close": [1.635, 1.638, 1.639, 1.640],
        "volume": [1000, 1200, 1100, 1300],
    }
    df = pd.DataFrame(data)

    fg = FeatureGenerator(df)
    df_features = fg.generate_all_features()
    print(df_features.head())