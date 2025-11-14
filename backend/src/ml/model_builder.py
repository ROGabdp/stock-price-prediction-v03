"""
LSTM 模型建構器
提供建構 LSTM 神經網路模型的函式
"""
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import Tuple


def build_lstm_model(
    input_shape: Tuple[int, int],
    lstm_units_1: int = 64,
    lstm_units_2: int = 32,
    dropout: float = 0.2,
    learning_rate: float = 0.001,
) -> Sequential:
    """
    建構 LSTM 模型

    參數:
        input_shape: 輸入形狀 (timesteps, features)
        lstm_units_1: 第一層 LSTM 單元數
        lstm_units_2: 第二層 LSTM 單元數
        dropout: Dropout 比例
        learning_rate: 學習率

    回傳:
        已編譯的 Keras Sequential 模型
    """
    model = Sequential(
        [
            # 第一層 LSTM（return_sequences=True 以連接第二層 LSTM）
            LSTM(
                lstm_units_1,
                return_sequences=True,
                input_shape=input_shape,
                name="lstm_1",
            ),
            Dropout(dropout, name="dropout_1"),
            # 第二層 LSTM
            LSTM(lstm_units_2, return_sequences=False, name="lstm_2"),
            Dropout(dropout, name="dropout_2"),
            # 全連接層
            Dense(25, activation="relu", name="dense_1"),
            # 輸出層（預測單一數值：收盤價）
            Dense(1, name="output"),
        ]
    )

    # 編譯模型
    model.compile(
        optimizer="adam",
        loss="mean_squared_error",
        metrics=["mean_absolute_error"],
    )

    return model


def get_model_summary(model: Sequential) -> str:
    """
    取得模型摘要

    參數:
        model: Keras 模型

    回傳:
        模型摘要字串
    """
    import io

    stream = io.StringIO()
    model.summary(print_fn=lambda x: stream.write(x + "\n"))
    return stream.getvalue()
