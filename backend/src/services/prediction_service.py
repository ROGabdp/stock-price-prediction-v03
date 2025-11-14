"""
預測服務
包含驗證預測請求、載入歷史資料、執行預測、格式化結果
"""
import pandas as pd
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from services.model_service import get_model_service
from services.metadata_service import get_metadata_service
from models.prediction import PredictionRequest, PredictionResult, HistoricalDataPoint
from ml.predictor import ModelPredictor
from ml.data_preprocessor import DataPreprocessor
from utils.date_utils import parse_date, format_date_iso, get_current_datetime_iso


class PredictionService:
    """預測服務"""

    def __init__(self):
        self.model_service = get_model_service()
        self.metadata_service = get_metadata_service()

    def predict(
        self,
        model_id: str,
        data_file_id: str,
        start_date: str,
    ) -> PredictionResult:
        """
        執行預測

        參數:
            model_id: 模型 ID
            data_file_id: 資料檔案 ID
            start_date: 預測起始日期 (YYYY-MM-DD)

        回傳:
            PredictionResult 物件

        拋出:
            ValueError: 若驗證失敗
        """
        start_time = time.time()

        # 1. 驗證請求
        self._validate_request(model_id, data_file_id, start_date)

        # 2. 載入模型資訊
        model_info = self.model_service.get_model(model_id)
        data_file = self.metadata_service.get_data_file(data_file_id)

        # 3. 載入 Keras 模型
        keras_model = self.model_service.load_keras_model(model_id)

        # 4. 載入歷史資料
        df = pd.read_csv(data_file["filePath"])

        # 5. 準備預處理器（需要重建以載入訓練時的 scaler）
        preprocessor = DataPreprocessor(
            lookback_window=model_info.hyperparameters.get("lookbackWindow", 60)
        )
        # 使用訓練資料重新擬合 scaler
        preprocessor.preprocess_data(Path(data_file["filePath"]))

        # 6. 建立預測器
        predictor = ModelPredictor(keras_model, preprocessor)

        # 7. 執行預測
        predictions = predictor.predict(
            df=df,
            start_date=start_date,
            prediction_days=model_info.prediction_days,
        )

        # 8. 準備歷史資料（用於圖表顯示）
        historical_data = self._prepare_historical_data(df, start_date)

        # 9. 建立回應
        execution_time = time.time() - start_time

        result = PredictionResult(
            request_info={
                "modelId": model_id,
                "modelName": model_info.model_name,
                "dataFileId": data_file_id,
                "startDate": start_date,
                "predictionDays": model_info.prediction_days,
            },
            historical_data=historical_data,
            predictions=predictions,
            metadata={
                "predictedAt": get_current_datetime_iso(),
                "executionTime": round(execution_time, 2),
            },
        )

        return result

    def _validate_request(
        self,
        model_id: str,
        data_file_id: str,
        start_date: str,
    ) -> None:
        """
        驗證預測請求

        參數:
            model_id: 模型 ID
            data_file_id: 資料檔案 ID
            start_date: 預測起始日期

        拋出:
            ValueError: 若驗證失敗
        """
        # 驗證模型存在
        model_info = self.model_service.get_model(model_id)
        if not model_info:
            raise ValueError(f"找不到模型: {model_id}")

        if model_info.status != "ready":
            raise ValueError("模型狀態不是 ready，無法執行預測")

        # 驗證資料檔案存在
        data_file = self.metadata_service.get_data_file(data_file_id)
        if not data_file:
            raise ValueError(f"找不到資料檔案: {data_file_id}")

        if data_file.get("status") != "valid":
            raise ValueError("資料檔案狀態無效")

        # 驗證日期格式
        parsed_date = parse_date(start_date)
        if not parsed_date:
            raise ValueError(f"日期格式錯誤: {start_date}")

        # 驗證日期範圍
        file_start = parse_date(data_file["dateRange"]["start"])
        file_end = parse_date(data_file["dateRange"]["end"])

        if not (file_start <= parsed_date <= file_end):
            raise ValueError(
                f"預測起始日期必須在資料範圍內 "
                f"({data_file['dateRange']['start']} 至 {data_file['dateRange']['end']})"
            )

    def _prepare_historical_data(
        self,
        df: pd.DataFrame,
        start_date: str,
    ) -> list:
        """
        準備歷史資料（用於圖表）

        參數:
            df: 歷史資料 DataFrame
            start_date: 預測起始日期

        回傳:
            HistoricalDataPoint 列表
        """
        # 只取預測起始日期之前的資料
        df['date_parsed'] = pd.to_datetime(df['date'])
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')

        historical_df = df[df['date_parsed'] < start_date_dt]

        # 限制資料點數量（最多 200 個點，避免圖表過於擁擠）
        if len(historical_df) > 200:
            # 等間隔取樣
            step = len(historical_df) // 200
            historical_df = historical_df.iloc[::step]

        historical_data = []
        for _, row in historical_df.iterrows():
            point = HistoricalDataPoint(
                date=format_date_iso(row['date_parsed'].date()),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume']),
            )
            historical_data.append(point)

        return historical_data


# 全域單例
_prediction_service_instance = None


def get_prediction_service() -> PredictionService:
    """取得預測服務單例"""
    global _prediction_service_instance
    if _prediction_service_instance is None:
        _prediction_service_instance = PredictionService()
    return _prediction_service_instance
