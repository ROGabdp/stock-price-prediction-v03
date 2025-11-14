"""
超參數調整模組
使用 Keras Tuner 進行超參數搜索
"""
import keras_tuner as kt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import Tuple


def build_tunable_model(hp: kt.HyperParameters, input_shape: Tuple[int, int]) -> Sequential:
    """
    建構可調整超參數的模型

    參數:
        hp: Keras Tuner HyperParameters 物件
        input_shape: 輸入形狀 (timesteps, features)

    回傳:
        已編譯的 Keras 模型
    """
    # 定義超參數搜索空間
    lstm_units_1 = hp.Int("lstm_units_1", min_value=32, max_value=128, step=32)
    lstm_units_2 = hp.Int("lstm_units_2", min_value=16, max_value=64, step=16)
    dropout = hp.Float("dropout", min_value=0.1, max_value=0.5, step=0.1)
    learning_rate = hp.Choice("learning_rate", values=[0.001, 0.01, 0.0001])

    model = Sequential(
        [
            LSTM(
                lstm_units_1,
                return_sequences=True,
                input_shape=input_shape,
            ),
            Dropout(dropout),
            LSTM(lstm_units_2, return_sequences=False),
            Dropout(dropout),
            Dense(25, activation="relu"),
            Dense(1),
        ]
    )

    # 編譯模型
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mean_squared_error",
        metrics=["mean_absolute_error"],
    )

    return model


def create_hyperparameter_tuner(
    input_shape: Tuple[int, int],
    project_name: str,
    max_epochs: int = 50,
    executions_per_trial: int = 1,
) -> kt.Hyperband:
    """
    建立 Keras Tuner Hyperband 超參數調整器

    參數:
        input_shape: 輸入形狀
        project_name: 專案名稱（用於儲存調整結果）
        max_epochs: 最大訓練週期數
        executions_per_trial: 每個試驗的執行次數

    回傳:
        Keras Tuner Hyperband 物件
    """
    # 定義模型建構函式（包裝以傳遞 input_shape）
    def model_builder(hp):
        return build_tunable_model(hp, input_shape)

    # 建立 Hyperband 調整器
    tuner = kt.Hyperband(
        model_builder,
        objective="val_loss",
        max_epochs=max_epochs,
        factor=3,  # 減少搜索空間的因子
        directory="hyperparameter_tuning",
        project_name=project_name,
        executions_per_trial=executions_per_trial,
        overwrite=True,  # 覆蓋先前的結果
    )

    return tuner


def get_best_hyperparameters(tuner: kt.Hyperband) -> dict:
    """
    取得最佳超參數

    參數:
        tuner: 已完成搜索的 Keras Tuner 物件

    回傳:
        最佳超參數字典
    """
    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

    return {
        "lstmUnits1": best_hps.get("lstm_units_1"),
        "lstmUnits2": best_hps.get("lstm_units_2"),
        "dropout": best_hps.get("dropout"),
        "learningRate": best_hps.get("learning_rate"),
    }
