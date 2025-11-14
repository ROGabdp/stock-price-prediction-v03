"""
模型預測器
包含載入模型、資料預處理、執行預測、機率計算、預測股價計算邏輯
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta

from ml.data_preprocessor import DataPreprocessor
from models.prediction import PredictionDataPoint
from utils.date_utils import format_date_iso


class ModelPredictor:
    """模型預測器"""

    def __init__(self, model, preprocessor: DataPreprocessor):
        """
        初始化預測器

        參數:
            model: Keras 模型
            preprocessor: 資料預處理器（包含訓練時的 scaler）
        """
        self.model = model
        self.preprocessor = preprocessor

    def predict(
        self,
        df: pd.DataFrame,
        start_date: str,
        prediction_days: int,
    ) -> List[PredictionDataPoint]:
        """
        執行預測

        參數:
            df: 歷史資料 DataFrame
            start_date: 預測起始日期 (YYYY-MM-DD)
            prediction_days: 預測天數

        回傳:
            預測資料點列表
        """
        predictions = []

        # 找到起始日期在 DataFrame 中的索引
        df['date_parsed'] = pd.to_datetime(df['date'])
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')

        # 找到最接近的日期索引
        start_idx = df[df['date_parsed'] >= start_date_dt].index[0]

        # 準備預測資料
        X = self.preprocessor.prepare_prediction_data(df, start_idx)

        if X is None:
            raise ValueError("預測起始日期之前的資料不足")

        # 逐日預測
        current_date = start_date_dt
        previous_close = float(df.iloc[start_idx - 1]['close'])

        for day in range(prediction_days):
            # 執行預測
            pred_normalized = self.model.predict(X, verbose=0)[0][0]

            # 反正規化
            pred_close = self._inverse_transform_single(pred_normalized)

            # 計算漲跌機率（簡化版：基於預測值與前一日收盤價的關係）
            up_probability = self._calculate_up_probability(pred_close, previous_close)

            # 計算變化百分比
            change_percent = ((pred_close - previous_close) / previous_close) * 100

            # 建立預測資料點
            pred_point = PredictionDataPoint(
                date=format_date_iso(current_date.date()),
                predicted_close=float(pred_close),
                up_probability=float(up_probability),
                change_percent=float(change_percent),
            )

            predictions.append(pred_point)

            # 更新前一日收盤價
            previous_close = pred_close

            # 下一天
            current_date += timedelta(days=1)

            # 更新輸入序列（滾動窗口）
            # 注意：這是簡化實作，實際應使用預測值更新輸入
            # 此處暫不實作多步預測的複雜邏輯

        return predictions

    def _inverse_transform_single(self, normalized_value: float) -> float:
        """
        反正規化單一預測值

        參數:
            normalized_value: 正規化後的值

        回傳:
            反正規化後的值
        """
        # 建立 dummy 陣列
        dummy = np.zeros((1, len(self.preprocessor.feature_columns)))
        dummy[0, 3] = normalized_value  # close price 在索引 3

        # 反轉換
        inverse_scaled = self.preprocessor.scaler.inverse_transform(dummy)

        return inverse_scaled[0, 3]

    def _calculate_up_probability(self, predicted_close: float, previous_close: float) -> float:
        """
        計算漲的機率

        參數:
            predicted_close: 預測收盤價
            previous_close: 前一日收盤價

        回傳:
            漲的機率 (0-1)
        """
        # 簡化實作：基於預測變化幅度轉換為機率
        change = (predicted_close - previous_close) / previous_close

        # 使用 sigmoid 函式將變化率轉換為機率
        # sigmoid(x) = 1 / (1 + exp(-k*x))，k 控制陡峭度
        k = 20  # 調整係數
        probability = 1 / (1 + np.exp(-k * change))

        # 限制在 0.1 到 0.9 之間，避免過度自信
        probability = np.clip(probability, 0.1, 0.9)

        return float(probability)
