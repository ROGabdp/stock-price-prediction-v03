"""
日誌記錄工具
配置 Python logging 模組，寫入至 backend/logs/app.log 和 backend/logs/training.log
"""
import logging
from pathlib import Path
from datetime import datetime

# 日誌目錄
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 日誌檔案路徑
APP_LOG_FILE = LOGS_DIR / "app.log"
TRAINING_LOG_FILE = LOGS_DIR / "training.log"


def setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    """
    設定日誌記錄器

    參數:
        name: 記錄器名稱
        log_file: 日誌檔案路徑
        level: 日誌層級

    回傳:
        logging.Logger 實例
    """
    # 建立 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重複新增 handler
    if logger.handlers:
        return logger

    # 建立檔案 handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    # 建立 console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 建立格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 設定格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 新增 handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 應用程式日誌記錄器
app_logger = setup_logger("app", APP_LOG_FILE, logging.INFO)

# 訓練日誌記錄器
training_logger = setup_logger("training", TRAINING_LOG_FILE, logging.INFO)


def get_app_logger() -> logging.Logger:
    """取得應用程式日誌記錄器"""
    return app_logger


def get_training_logger() -> logging.Logger:
    """取得訓練日誌記錄器"""
    return training_logger


def log_training_start(model_name: str, data_file_id: str, prediction_days: int, hyperparameters: dict):
    """
    記錄訓練開始

    參數:
        model_name: 模型名稱
        data_file_id: 資料檔案 ID
        prediction_days: 預測天數
        hyperparameters: 超參數字典
    """
    training_logger.info("=" * 60)
    training_logger.info(f"訓練開始: {model_name}")
    training_logger.info(f"資料檔案: {data_file_id}")
    training_logger.info(f"預測天數: {prediction_days}")
    training_logger.info(f"超參數: {hyperparameters}")
    training_logger.info("=" * 60)


def log_training_complete(
    model_name: str,
    model_id: str,
    train_loss: float,
    val_loss: float,
    train_mae: float,
    val_mae: float,
    execution_time: float,
):
    """
    記錄訓練完成

    參數:
        model_name: 模型名稱
        model_id: 模型 ID
        train_loss: 訓練損失
        val_loss: 驗證損失
        train_mae: 訓練 MAE
        val_mae: 驗證 MAE
        execution_time: 執行時間（秒）
    """
    training_logger.info("=" * 60)
    training_logger.info(f"訓練完成: {model_name}")
    training_logger.info(f"模型 ID: {model_id}")
    training_logger.info(f"訓練損失: {train_loss:.6f}")
    training_logger.info(f"驗證損失: {val_loss:.6f}")
    training_logger.info(f"訓練 MAE: {train_mae:.6f}")
    training_logger.info(f"驗證 MAE: {val_mae:.6f}")
    training_logger.info(f"執行時間: {execution_time:.2f} 秒")
    training_logger.info("=" * 60)


def log_training_error(model_name: str, error_message: str):
    """
    記錄訓練錯誤

    參數:
        model_name: 模型名稱
        error_message: 錯誤訊息
    """
    training_logger.error("=" * 60)
    training_logger.error(f"訓練失敗: {model_name}")
    training_logger.error(f"錯誤訊息: {error_message}")
    training_logger.error("=" * 60)


def log_api_request(method: str, endpoint: str, status_code: int):
    """
    記錄 API 請求

    參數:
        method: HTTP 方法
        endpoint: 端點路徑
        status_code: 狀態碼
    """
    app_logger.info(f"{method} {endpoint} - {status_code}")


def log_api_error(method: str, endpoint: str, error_message: str):
    """
    記錄 API 錯誤

    參數:
        method: HTTP 方法
        endpoint: 端點路徑
        error_message: 錯誤訊息
    """
    app_logger.error(f"{method} {endpoint} - 錯誤: {error_message}")
