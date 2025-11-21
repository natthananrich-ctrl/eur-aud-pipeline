"""
live_predictor.py
-----------------
Predictor แบบ real-time พร้อม AuditLogger + Config Management
"""

import pandas as pd
from project.utils.logger import AuditLogger
from project.utils.config_loader import load_config
from project.features.feature_generator import FeatureGenerator
from project.models.model_selector import ModelSelector
from project.news.news_connector import NewsConnector
from project.news.news_filter import NewsFilter
from project.news.sentiment_analyzer import SentimentAnalyzer

class LivePredictor:
    def __init__(self, env="prod"):
        self.logger = AuditLogger()
        self.config = load_config(env=env)
        model_path = self.config["model"]["save_path"] + "best_model.pkl"
        self.model_selector = ModelSelector.load_best_model(model_path)

    def predict_signal(self):
        try:
            # 1. โหลดข้อมูลล่าสุดจาก config
            data_path = self.config["data"]["source_path"]
            df_latest = pd.read_csv(data_path)

            fg = FeatureGenerator(df_latest)
            df_features = fg.generate_all_features()
            self.logger.log_event("live", "generate_features", "SUCCESS", "Features generated for latest candle")

            # 2. โหลดข่าวและ sentiment
            news_path = self.config["data"]["news_path"]
            connector = NewsConnector(source="csv", path_or_url=news_path)
            df_news = connector.load_news()

            nf = NewsFilter(df_news, symbol=self.config["backtest"]["symbol"], window_minutes=30)
            analyzer = SentimentAnalyzer()
            df_news = analyzer.analyze_dataframe(df_news, text_col="event")
            sentiment_summary = df_news["sentiment"].tail(1).values[0]
            self.logger.log_event("live", "sentiment_analysis", "SUCCESS", f"latest_sentiment={sentiment_summary}")

            # 3. ใช้โมเดลทำนาย
            signal = self.model_selector.predict(df_features.tail(1))
            action = "BUY" if signal == 1 else "SELL"
            self.logger.log_event("live", "predict_signal", "SUCCESS", f"signal={action}, sentiment={sentiment_summary}")

            print(f"✅ Live signal: {action} (sentiment={sentiment_summary})")
            return action

        except Exception as e:
            self.logger.log_event("live", "predict_signal", "FAIL", str(e))
            raise


if __name__ == "__main__":
    predictor = LivePredictor(env="prod")  # เลือก environment ได้: dev/test/prod
    predictor.predict_signal()