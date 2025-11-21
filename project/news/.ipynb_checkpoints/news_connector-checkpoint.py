"""
news_connector.py
-----------------
โมดูลสำหรับดึงข้อมูลข่าวเศรษฐกิจจาก API หรือไฟล์
แล้วแปลงให้อยู่ในรูปแบบ DataFrame ที่ใช้กับ NewsFilter
"""

import pandas as pd
import requests
import datetime

class NewsConnector:
    def __init__(self, source="csv", path_or_url=None):
        """
        Parameters
        ----------
        source : str
            "csv" หรือ "api"
        path_or_url : str
            path ของไฟล์ CSV หรือ URL ของ API
        """
        self.source = source
        self.path_or_url = path_or_url

    def load_news(self):
        """
        โหลดข่าวจาก source ที่กำหนด
        Returns
        -------
        pd.DataFrame
            คอลัมน์ ['datetime', 'currency', 'impact', 'event']
        """
        if self.source == "csv":
            df = pd.read_csv(self.path_or_url)
            df["datetime"] = pd.to_datetime(df["datetime"])
            return df

        elif self.source == "api":
            resp = requests.get(self.path_or_url)
            data = resp.json()

            # สมมติ API คืนค่าเป็น list ของ dict
            df = pd.DataFrame(data)
            df["datetime"] = pd.to_datetime(df["datetime"])
            return df

        else:
            raise ValueError("❌ Source ต้องเป็น 'csv' หรือ 'api'")


# ============================
# ตัวอย่างการใช้งาน
# ============================
if __name__ == "__main__":
    # ตัวอย่างโหลดจาก CSV
    connector = NewsConnector(source="csv", path_or_url="project/data/news.csv")
    df_news = connector.load_news()
    print("✅ Loaded news events:", df_news.head())

    # ตัวอย่างโหลดจาก API (สมมติ)
    # connector = NewsConnector(source="api", path_or_url="https://api.example.com/economic_calendar")
    # df_news = connector.load_news()
    # print(df_news.head())