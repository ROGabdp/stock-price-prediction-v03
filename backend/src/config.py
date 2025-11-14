"""
配置管理模組
提供系統配置常數與路徑設定
"""
import os
from pathlib import Path

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent.absolute()

# 資料儲存路徑
DATA_DIR = BASE_DIR / "data"
UPLOADED_DATA_DIR = DATA_DIR / "uploaded"
METADATA_FILE = DATA_DIR / "metadata.json"

# 模型儲存路徑
MODELS_DIR = BASE_DIR / "models"

# 日誌路徑
LOGS_DIR = BASE_DIR / "logs"
APP_LOG_FILE = LOGS_DIR / "app.log"
TRAINING_LOG_FILE = LOGS_DIR / "training.log"

# 檔案大小限制（位元組）
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB

# 資料驗證常數
MIN_DATA_ROWS = 60  # 最少資料筆數
MAX_DATA_ROWS = 1_000_000  # 最多資料筆數

# CSV 必要欄位
REQUIRED_CSV_COLUMNS = ["date", "open", "high", "low", "close", "volume"]

# LSTM 模型參數
DEFAULT_LOOKBACK_WINDOW = 60  # 預設回看窗口（天數）
MIN_PREDICTION_DAYS = 1  # 最少預測天數
MAX_PREDICTION_DAYS = 30  # 最多預測天數

# Flask 配置
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# CORS 配置
CORS_ORIGINS = "*"  # 開發環境允許所有來源，生產環境應限制

# 確保必要目錄存在
def ensure_directories():
    """確保所有必要目錄存在"""
    UPLOADED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


# 初始化時自動建立目錄
ensure_directories()
