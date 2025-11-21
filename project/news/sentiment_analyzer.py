"""
sentiment_analyzer.py
---------------------
โมดูลสำหรับวิเคราะห์ sentiment ของข้อความข่าว
ใช้ NLP แปลงข้อความเป็นคะแนน sentiment (positive/negative/neutral)
"""

import pandas as pd
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self):
        pass

    def analyze_text(self, text: str):
        """
        วิเคราะห์ข้อความข่าวและคืนค่า sentiment
        Returns
        -------
        dict : {"polarity": float, "subjectivity": float, "sentiment": str}
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity   # -1 ถึง 1
        subjectivity = blob.sentiment.subjectivity  # 0 ถึง 1

        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment
        }

    def analyze_dataframe(self, df: pd.DataFrame, text_col="event"):
        """
        วิเคราะห์ข้อความข่าวใน DataFrame
        Parameters
        ----------
        df : pd.DataFrame
            ต้องมีคอลัมน์ข้อความ เช่น 'event'
        text_col : str
            ชื่อคอลัมน์ที่เก็บข้อความข่าว
        Returns
        -------
        pd.DataFrame : เพิ่มคอลัมน์ polarity, subjectivity, sentiment
        """
        results = df[text_col].apply(self.analyze_text)
        df["polarity"] = results.apply(lambda x: x["polarity"])
        df["subjectivity"] = results.apply(lambda x: x["subjectivity"])
        df["sentiment"] = results.apply(lambda x: x["sentiment"])
        return df


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    data = {
        "datetime": ["2025-11-20 16:00:00", "2025-11-20 16:30:00"],
        "currency": ["EUR", "AUD"],
        "impact": ["High", "Medium"],
        "event": ["ECB announces rate hike", "RBA warns of economic slowdown"],
    }
    df_news = pd.DataFrame(data)

    analyzer = SentimentAnalyzer()
    df_result = analyzer.analyze_dataframe(df_news, text_col="event")

    print("✅ Sentiment Analysis Results:")
    print(df_result[["event", "sentiment", "polarity", "subjectivity"]])