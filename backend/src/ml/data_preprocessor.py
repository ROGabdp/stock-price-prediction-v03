"""
資料預處理模組
包含時間序列視窗切割、正規化、訓練/驗證集分割
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List, Optional
from pathlib import Path

from config import DEFAULT_LOOKBACK_WINDOW


class DataPreprocessor:
    """資料預處理器"""

    def __init__(self, lookback_window: int = DEFAULT_LOOKBACK_WINDOW):
        """
        初始化資料預處理器

        參數:
            lookback_window: 回看窗口大小（預設 60 天）
        """
        self.lookback_window = lookback_window
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns: List[str] = []

    def preprocess_data(
        self, csv_path: Path, validation_split: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        完整預處理流程

        參數:
            csv_path: CSV 檔案路徑
            validation_split: 驗證集分割比例（預設 0.2）

        回傳:
            (X_train, X_val, y_train, y_val)
        """
        # 1. 載入 CSV
        df = pd.read_csv(csv_path)

        # 2. 選擇特徵欄位
        self.feature_columns = self._select_features(df)

        # 3. 提取特徵資料
        data = df[self.feature_columns].values

        # 4. 正規化資料
        scaled_data = self.scaler.fit_transform(data)

        # 5. 建立時間序列視窗
        X, y = self._create_sequences(scaled_data)

        # 6. 分割訓練/驗證集
        X_train, X_val, y_train, y_val = self._train_val_split(
            X, y, validation_split
        )

        return X_train, X_val, y_train, y_val

    def _select_features(self, df: pd.DataFrame) -> List[str]:
        """
        選擇特徵欄位

        參數:
            df: pandas DataFrame

        回傳:
            特徵欄位列表
        """
        # 必要欄位
        required_features = ["open", "high", "low", "close", "volume"]

        # 可選技術指標
        optional_features = [
            "SMA5",
            "SMA10",
            "SMA20",
            "SMA60",
            "MA5",
            "MA10",
            "DIF12-26",
            "MACD9",
            "K(9,3)",
            "D(9,3)",
        ]

        # 選擇存在的欄位
        features = required_features.copy()
        for col in optional_features:
            if col in df.columns:
                features.append(col)

        return features

    def _create_sequences(
        self, scaled_data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        建立時間序列視窗

        參數:
            scaled_data: 已正規化的資料

        回傳:
            (X, y) - 輸入序列與目標值
        """
        X, y = [], []

        for i in range(self.lookback_window, len(scaled_data)):
            # 輸入：過去 lookback_window 天的所有特徵
            X.append(scaled_data[i - self.lookback_window : i])
            # 目標：當天的收盤價（假設 close 是第 4 個欄位，索引 3）
            y.append(scaled_data[i, 3])  # close price

        return np.array(X), np.array(y)

    def _train_val_split(
        self, X: np.ndarray, y: np.ndarray, validation_split: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        分割訓練/驗證集

        參數:
            X: 輸入資料
            y: 目標值
            validation_split: 驗證集比例

        回傳:
            (X_train, X_val, y_train, y_val)
        """
        split_idx = int(len(X) * (1 - validation_split))

        X_train = X[:split_idx]
        X_val = X[split_idx:]
        y_train = y[:split_idx]
        y_val = y[split_idx:]

        return X_train, X_val, y_train, y_val

    def inverse_transform_predictions(self, predictions: np.ndarray) -> np.ndarray:
        """
        將預測結果反正規化回原始股價尺度

        參數:
            predictions: 正規化後的預測值

        回傳:
            反正規化後的預測值
        """
        # 建立與原始資料相同形狀的陣列
        dummy = np.zeros((len(predictions), len(self.feature_columns)))
        # 將預測值放入 close price 欄位（索引 3）
        dummy[:, 3] = predictions.flatten()

        # 反轉換
        inverse_scaled = self.scaler.inverse_transform(dummy)

        # 回傳 close price 欄位
        return inverse_scaled[:, 3]

    def get_input_shape(self) -> Tuple[int, int]:
        """
        取得模型輸入形狀

        回傳:
            (timesteps, features)
        """
        return (self.lookback_window, len(self.feature_columns))

    def prepare_prediction_data(
        self, df: pd.DataFrame, start_idx: int
    ) -> Optional[np.ndarray]:
        """
        準備預測用的資料

        參數:
            df: pandas DataFrame
            start_idx: 預測起始索引

        回傳:
            正規化後的輸入資料，若資料不足則回傳 None
        """
        # 檢查資料是否足夠
        if start_idx < self.lookback_window:
            return None

        # 提取特徵
        data = df[self.feature_columns].values

        # 正規化（使用訓練時的 scaler）
        scaled_data = self.scaler.transform(data)

        # 提取預測起始日期之前的 lookback_window 天資料
        X = scaled_data[start_idx - self.lookback_window : start_idx]

        # 重塑為 (1, timesteps, features)
        X = X.reshape(1, self.lookback_window, len(self.feature_columns))

        return X
