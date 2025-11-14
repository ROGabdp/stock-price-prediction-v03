# 股價漲跌機率預測系統

使用 LSTM 神經網路從歷史股價資料中學習，預測未來 1-30 天的股價漲跌機率與幅度。

## 專案簡介

本系統提供完整的股價預測解決方案，包含：
- **模型訓練**: 使用 LSTM 神經網路自動訓練預測模型，支援超參數自動調整
- **股價預測**: 選擇已訓練模型，預測未來 N 天的股價走勢與漲跌機率
- **資料管理**: 上傳、管理歷史股價 CSV 資料檔案
- **視覺化**: 使用互動式圖表同時顯示歷史股價與預測結果

## 技術堆疊

### 後端
- **語言**: Python 3.11+
- **Web 框架**: Flask 3.0.0
- **機器學習**: TensorFlow 2.15.0 + Keras
- **超參數調整**: Keras Tuner 1.4.6
- **資料處理**: pandas 2.1.4

### 前端
- **語言**: JavaScript (ES6+)
- **框架**: 原生 JavaScript (無框架)
- **圖表**: Chart.js 4.4.0

### 儲存
- **資料儲存**: 檔案系統 + JSON 元資料
- **模型格式**: TensorFlow SavedModel (.keras)

## 快速開始

### 環境需求

- Python 3.11 或以上
- 至少 8GB RAM (建議 16GB)
- 5GB 可用磁碟空間

### 安裝步驟

#### 1. 建立 Python 虛擬環境

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. 安裝後端依賴套件

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 啟動後端伺服器

```bash
cd backend/src
python app.py
```

後端將運行於 `http://localhost:5000`

#### 4. 啟動前端 (開啟新的終端機)

**方法 1: Python 簡易伺服器**
```bash
cd frontend
python -m http.server 8000
```

**方法 2: 直接開啟 HTML**
- 直接在瀏覽器中開啟 `frontend/index.html`

前端將運行於 `http://localhost:8000`

### 使用範例資料

專案根目錄包含範例 CSV 檔案 `19940513-20251111-converted.csv`，包含台股歷史資料 (1994-2025)，可用於測試系統功能。

## 專案結構

```
stock-price-prediction-v03/
├── backend/                  # 後端專案
│   ├── src/                  # 後端原始碼
│   │   ├── api/              # API 路由層
│   │   ├── models/           # 資料模型 (dataclass)
│   │   ├── services/         # 業務邏輯層
│   │   ├── ml/               # 機器學習模組
│   │   ├── utils/            # 工具函式
│   │   └── app.py            # Flask 應用程式進入點
│   ├── data/                 # 資料儲存
│   │   ├── uploaded/         # 上傳的 CSV 檔案
│   │   └── metadata.json     # 元資料
│   ├── models/               # 訓練模型儲存
│   ├── logs/                 # 日誌
│   └── requirements.txt      # Python 依賴套件
│
├── frontend/                 # 前端專案
│   ├── index.html            # 首頁
│   ├── pages/                # 功能頁面
│   ├── css/                  # 樣式檔案
│   └── js/                   # JavaScript 模組
│
├── specs/                    # 規格文件
│   └── 001-stock-price-prediction/
│       ├── spec.md           # 功能規格
│       ├── plan.md           # 實作計畫
│       ├── data-model.md     # 資料模型
│       ├── tasks.md          # 任務清單
│       └── contracts/        # API 合約
│
├── 19940513-20251111-converted.csv  # 範例資料
├── CLAUDE.md                 # Claude Code 指南
└── README.md                 # 本檔案
```

## API 端點

**Base URL**: `http://localhost:5000/api`

### 資料管理
- `POST /data/upload` - 上傳 CSV 檔案
- `GET /data/files` - 取得資料檔案清單
- `DELETE /data/files/{fileId}` - 刪除資料檔案

### 模型訓練
- `POST /models/train` - 啟動模型訓練
- `GET /models/training/tasks/{taskId}` - 查詢訓練進度

### 模型管理
- `GET /models` - 取得模型清單
- `GET /models/{modelId}` - 取得模型詳情
- `DELETE /models/{modelId}` - 刪除模型

### 預測執行
- `POST /predict` - 執行預測
- `POST /predict/compare` - 比較多個模型預測結果

完整 API 規格請參考 `specs/001-stock-price-prediction/contracts/api.yaml`

## CSV 資料格式

### 必要欄位
- `date`: 交易日期 (YYYY/M/D 或 YYYY-MM-DD 格式)
- `open`: 開盤價
- `high`: 最高價
- `low`: 最低價
- `close`: 收盤價
- `volume`: 成交量

### 可選技術指標欄位
- SMA5, SMA10, SMA20, SMA60, SMA120, SMA240
- MA5, MA10
- DIF12-26, MACD9, OSC
- K(9,3), D(9,3)
- net buy sell, cumulative net buy sell, buy, sell

### 資料要求
- 至少 60 筆歷史資料
- 檔案大小限制: 100MB
- 日期不可重複

## 開發指令

### 程式碼格式化
```bash
# Python (使用 black)
cd backend
black src

# 程式碼檢查 (使用 flake8)
flake8 src
```

## 文件

- **功能規格**: `specs/001-stock-price-prediction/spec.md`
- **實作計畫**: `specs/001-stock-price-prediction/plan.md`
- **資料模型**: `specs/001-stock-price-prediction/data-model.md`
- **快速入門**: `specs/001-stock-price-prediction/quickstart.md`
- **Claude Code 指南**: `CLAUDE.md`

## 授權

本專案僅供學習與研究使用。

## 貢獻

歡迎提出問題與建議！請透過 GitHub Issues 回報問題。

---

**建立日期**: 2025-11-14
**版本**: 1.0.0
