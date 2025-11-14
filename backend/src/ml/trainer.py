"""
模型訓練器
包含訓練流程、Keras Tuner 整合、模型儲存、進度回調
"""
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import Callback, EarlyStopping

from ml.model_builder import build_lstm_model
from ml.hyperparameter_tuner import create_hyperparameter_tuner, get_best_hyperparameters
from ml.data_preprocessor import DataPreprocessor
from config import DEFAULT_LOOKBACK_WINDOW


class TrainingProgressCallback(Callback):
    """訓練進度回調"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化

        參數:
            progress_callback: 進度回調函式 (epoch, logs)
        """
        super().__init__()
        self.progress_callback = progress_callback

    def on_epoch_end(self, epoch, logs=None):
        """每個 epoch 結束時呼叫"""
        if self.progress_callback:
            self.progress_callback(epoch + 1, logs)


class ModelTrainer:
    """模型訓練器"""

    def __init__(
        self,
        data_file_path: Path,
        lookback_window: int = DEFAULT_LOOKBACK_WINDOW,
        use_hyperparameter_tuning: bool = True,
    ):
        """
        初始化訓練器

        參數:
            data_file_path: 資料檔案路徑
            lookback_window: 回看窗口大小
            use_hyperparameter_tuning: 是否使用超參數調整
        """
        self.data_file_path = data_file_path
        self.lookback_window = lookback_window
        self.use_hyperparameter_tuning = use_hyperparameter_tuning
        self.preprocessor = DataPreprocessor(lookback_window)
        self.model: Optional[Sequential] = None
        self.history = None
        self.best_hyperparameters: Optional[Dict[str, Any]] = None

    def train(
        self,
        epochs: int = 50,
        batch_size: int = 32,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        訓練模型

        參數:
            epochs: 訓練週期數
            batch_size: 批次大小
            progress_callback: 進度回調函式

        回傳:
            訓練結果字典（包含指標與超參數）
        """
        start_time = time.time()

        # 1. 資料預處理
        print("正在預處理資料...")
        X_train, X_val, y_train, y_val = self.preprocessor.preprocess_data(
            self.data_file_path
        )

        print(f"訓練集大小: {X_train.shape}")
        print(f"驗證集大小: {X_val.shape}")

        input_shape = self.preprocessor.get_input_shape()

        # 2. 超參數調整（若啟用）
        if self.use_hyperparameter_tuning:
            print("正在進行超參數調整...")
            self.best_hyperparameters = self._tune_hyperparameters(
                X_train, y_train, X_val, y_val, input_shape
            )
        else:
            # 使用預設超參數
            self.best_hyperparameters = {
                "lstmUnits1": 64,
                "lstmUnits2": 32,
                "dropout": 0.2,
                "learningRate": 0.001,
            }

        # 3. 建構最終模型
        print("正在建構模型...")
        self.model = build_lstm_model(
            input_shape=input_shape,
            lstm_units_1=self.best_hyperparameters["lstmUnits1"],
            lstm_units_2=self.best_hyperparameters["lstmUnits2"],
            dropout=self.best_hyperparameters["dropout"],
            learning_rate=self.best_hyperparameters["learningRate"],
        )

        # 4. 訓練模型
        print("正在訓練模型...")
        callbacks = [
            TrainingProgressCallback(progress_callback),
            EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        ]

        self.history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        # 5. 評估模型
        train_loss, train_mae = self.model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_mae = self.model.evaluate(X_val, y_val, verbose=0)

        training_duration = time.time() - start_time

        print(f"訓練完成！耗時: {training_duration:.2f} 秒")
        print(f"訓練損失: {train_loss:.4f}, 訓練 MAE: {train_mae:.4f}")
        print(f"驗證損失: {val_loss:.4f}, 驗證 MAE: {val_mae:.4f}")

        # 6. 回傳結果
        return {
            "metrics": {
                "trainLoss": float(train_loss),
                "valLoss": float(val_loss),
                "trainMAE": float(train_mae),
                "valMAE": float(val_mae),
            },
            "hyperparameters": {
                **self.best_hyperparameters,
                "batchSize": batch_size,
                "epochs": len(self.history.history["loss"]),
                "lookbackWindow": self.lookback_window,
            },
            "trainingDuration": training_duration,
        }

    def _tune_hyperparameters(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        input_shape: tuple,
    ) -> Dict[str, Any]:
        """
        使用 Keras Tuner 調整超參數

        參數:
            X_train, y_train: 訓練資料
            X_val, y_val: 驗證資料
            input_shape: 輸入形狀

        回傳:
            最佳超參數字典
        """
        # 建立 tuner
        tuner = create_hyperparameter_tuner(
            input_shape=input_shape,
            project_name=f"tuning_{int(time.time())}",
            max_epochs=20,  # 減少調整時間
        )

        # 執行搜索
        tuner.search(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=20,
            batch_size=32,
            verbose=0,
        )

        # 取得最佳超參數
        best_hps = get_best_hyperparameters(tuner)

        return best_hps

    def save_model(self, model_path: Path) -> None:
        """
        儲存模型

        參數:
            model_path: 模型儲存路徑
        """
        if self.model is None:
            raise ValueError("模型尚未訓練")

        self.model.save(str(model_path))
        print(f"模型已儲存至: {model_path}")

    def get_preprocessor(self) -> DataPreprocessor:
        """取得預處理器（用於後續預測）"""
        return self.preprocessor
