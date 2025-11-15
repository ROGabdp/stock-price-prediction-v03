# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

股價漲跌機率預測系統 (Stock Price Prediction System) - 使用 LSTM 神經網路從歷史股價資料中學習，預測未來 1-30 天的股價漲跌機率與幅度。

**技術堆疊**:
- **後端**: Flask 3.0.0 + TensorFlow 2.15.0 + Keras Tuner 1.4.6 + pandas 2.1.4
- **前端**: 原生 JavaScript (ES6+) + Chart.js 4.4.0
- **儲存**: 檔案系統 + JSON 元資料
- **架構**: 前後端分離 RESTful API

**Python 版本**: 3.11+

## GPU 加速支援

本專案支援 **自動 GPU 偵測與加速**：
- **TensorFlow 版本**: 2.16.1 (支援 CPU 與 GPU)
- **GPU 支援**: NVIDIA GPU (CUDA 自動安裝)
- **自動偵測**: 啟動時自動偵測可用的 GPU 裝置
- **開發環境選項**:
  - **Windows (CPU)**: 使用 CPU 訓練，適合測試
  - **Windows + WSL2 (GPU)**: 推薦！使用 GPU 加速，設定簡單（參考 `WSL2-GPU-SETUP.md`）
  - **macOS/Linux**: 視硬體支援 CPU 或 GPU

### GPU 狀態查詢
啟動後端後，可透過以下 API 查詢 GPU 狀態：
```bash
curl http://localhost:5000/api/gpu-status
```

### 安裝 GPU 版本（可選）
```bash
# 如果有 NVIDIA GPU
pip uninstall tensorflow
pip install tensorflow[and-cuda]==2.16.1
```

詳細的 WSL2 GPU 設定請參考 `WSL2-GPU-SETUP.md`。

## 重要專案規則 (來自專案憲章)

### 語言與文件要求
- **必須使用正體中文**: 所有文件、程式碼註解、UI 文字、錯誤訊息、Git 提交訊息都必須使用正體中文
- **例外**: 程式碼識別符（變數名、函式名、類別名）使用英文，遵循各語言慣例

### 開發流程
- **規格驅動開發**: 任何功能開發前必須先完成 `spec.md`，實作必須基於規格文件
- **高品質可測試的 MVP**: 專注於交付 P1 優先級的核心功能
- **嚴格禁止過度設計**: 遵循 YAGNI 原則，選擇最簡單可行的方案

### 程式碼風格
- **Python**: 嚴格遵循 PEP 8 與 Pythonic 風格
  - 使用 `snake_case` 命名變數與函式
  - 使用 `PascalCase` 命名類別
  - 使用型別提示 (Type Hints)
  - 使用 dataclass 定義資料模型
  - 配置 black + flake8 (.flake8: max-line-length=88)
- **JavaScript**: 遵循 Idiomatic JavaScript
  - 使用 ES6+ 語法 (async/await、箭頭函式、解構)
  - 使用 `camelCase` 命名變數與函式
  - 使用 `PascalCase` 命名 React 元件

### API 命名規範
- **所有 API 介面使用 camelCase**: 端點參數、請求欄位、回應欄位都必須使用 `camelCase`
- 範例: `modelId`, `dataFileId`, `startDate`, `predictedClose`

## 專案結構

```
stock-price-prediction-v03/
├── backend/                          # 後端專案
│   ├── src/                          # 後端原始碼
│   │   ├── app.py                    # Flask 應用程式進入點
│   │   ├── config.py                 # 配置管理
│   │   ├── api/                      # API 路由層
│   │   │   ├── data_routes.py        # 資料管理 API
│   │   │   ├── model_routes.py       # 模型管理 API
│   │   │   ├── training_routes.py    # 模型訓練 API
│   │   │   └── prediction_routes.py  # 預測執行 API
│   │   ├── models/                   # 資料模型層 (dataclass)
│   │   │   ├── data_file.py
│   │   │   ├── prediction_model.py
│   │   │   ├── training_task.py
│   │   │   └── prediction.py
│   │   ├── services/                 # 業務邏輯層
│   │   │   ├── metadata_service.py   # 元資料 CRUD
│   │   │   ├── data_service.py       # 資料檔案服務
│   │   │   ├── training_service.py   # 訓練服務
│   │   │   └── prediction_service.py # 預測服務
│   │   ├── ml/                       # 機器學習模組
│   │   │   ├── model_builder.py      # LSTM 模型建構
│   │   │   ├── hyperparameter_tuner.py # Keras Tuner 超參數調整
│   │   │   ├── trainer.py            # 模型訓練邏輯
│   │   │   └── predictor.py          # 模型預測邏輯
│   │   └── utils/                    # 工具函式
│   │       ├── csv_validator.py      # CSV 驗證
│   │       ├── date_utils.py         # 日期處理
│   │       └── file_utils.py         # 檔案操作
│   ├── data/                         # 資料儲存
│   │   ├── uploaded/                 # CSV 檔案
│   │   └── metadata.json             # 元資料檔案
│   ├── models/                       # 訓練模型儲存 (.keras 檔案)
│   └── logs/                         # 日誌
│
├── frontend/                         # 前端專案
│   ├── index.html                    # 首頁 (導航選單)
│   ├── pages/                        # 功能頁面
│   │   ├── data-management.html
│   │   ├── model-training.html
│   │   ├── prediction.html
│   │   └── model-comparison.html
│   ├── css/                          # 樣式檔案
│   │   ├── style.css                 # 全域樣式
│   │   └── components.css            # 元件樣式
│   └── js/                           # JavaScript 模組
│       ├── api.js                    # Fetch API 封裝
│       ├── data-management.js
│       ├── model-training.js
│       ├── prediction.js
│       ├── chart-renderer.js         # Chart.js 圖表渲染
│       └── utils.js
│
└── specs/                            # 規格文件
    └── 001-stock-price-prediction/
        ├── spec.md                   # 功能規格
        ├── plan.md                   # 實作計畫
        ├── data-model.md             # 資料模型設計
        ├── tasks.md                  # 任務清單
        ├── quickstart.md             # 快速入門
        └── contracts/api.yaml        # OpenAPI 規格
```

## 架構設計原則

### 後端分層架構
1. **API 層** (`api/`): 處理 HTTP 請求/回應，路由定義
2. **業務邏輯層** (`services/`): 核心業務邏輯，與 API 層解耦
3. **資料模型層** (`models/`): dataclass 定義，資料結構與驗證
4. **ML 模組** (`ml/`): 機器學習專屬邏輯，獨立於業務邏輯
5. **工具層** (`utils/`): 可重用的工具函式

### 儲存架構
- **集中式元資料**: 所有元資料集中於 `backend/data/metadata.json`
- **檔案命名**: 使用 UUID 前綴確保唯一性 (例如: `file_{uuid}_{name}.csv`)
- **原子操作**: 更新 metadata.json 時先寫入臨時檔案，再重新命名
- **模型儲存**: .keras 格式，命名為 `model_{id}_{name}.keras`

### 前端架構
- **頁面分離**: 每個功能獨立 HTML 頁面，避免 SPA 複雜性
- **JavaScript 模組化**: 按功能拆分 JS 檔案
- **原生實作**: 不使用 React/Vue，使用原生 JavaScript + Fetch API

## 資料模型核心實體

1. **DataFile** - 上傳的 CSV 歷史股價資料
2. **HistoricalStockData** - CSV 內的股價記錄
3. **PredictionModel** - 訓練好的 LSTM 模型
4. **PredictionRequest** - 使用者發起的預測請求
5. **PredictionResult** - 模型預測輸出
6. **TrainingTask** - 模型訓練執行記錄
7. **HyperparameterConfiguration** - 模型超參數設定

詳細定義請參考 `specs/001-stock-price-prediction/data-model.md`

## CSV 資料格式

**必要欄位**:
- `date` (日期，YYYY/M/D 或 YYYY-MM-DD 格式)
- `open`, `high`, `low`, `close` (價格，必須 > 0)
- `volume` (成交量，>= 0)

**可選技術指標欄位**: SMA5, SMA10, SMA20, SMA60, SMA120, SMA240, MA5, MA10, DIF12-26, MACD9, OSC, K(9,3), D(9,3), net buy sell, cumulative net buy sell, buy, sell

範例檔案: `19940513-20251111-converted.csv`

## 常用開發指令

### 後端啟動（CPU 模式 - Windows）

```bash
# 建立虛擬環境（首次執行）
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate

# 安裝依賴
pip install -r backend/requirements.txt

# 啟動 Flask 開發伺服器
cd backend\src
python app.py
# 預設運行於 http://localhost:5000
```

### 後端啟動（GPU 模式 - WSL2）

```bash
# 啟動 WSL2（在 Windows PowerShell 中）
wsl -d Ubuntu_D  # 或 wsl（使用預設發行版）

# 切換到專案目錄
cd /mnt/d/000-github-repositories/stock-price-prediction-v03

# 建立虛擬環境（首次執行）
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install tensorflow[and-cuda]==2.16.1
pip install -r backend/requirements.txt

# 啟動虛擬環境（之後每次執行）
source venv/bin/activate

# 啟動 Flask 開發伺服器
cd backend/src
python3 app.py
# 預設運行於 http://localhost:5000
# 成功啟動會顯示 GPU 偵測訊息
```

### 前端

```bash
# 開啟前端 (使用本地伺服器或直接開啟 HTML)
# 方法 1: Python 簡易伺服器
cd frontend
python -m http.server 8000
# 訪問 http://localhost:8000

# 方法 2: 直接在瀏覽器開啟
# 開啟 frontend/index.html
```

### 程式碼品質工具

```bash
# 程式碼格式化
black backend/src

# 程式碼檢查
flake8 backend/src
```

## API 端點概覽

**Base URL**: `http://localhost:5000/api`

### 系統狀態
- `GET /api/health` - 健康檢查
- `GET /api/gpu-status` - 查詢 GPU 狀態

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

## 核心使用者故事 (User Stories)

### P1 優先級 (MVP 核心功能)
1. **訓練股價預測模型**: 使用者選擇資料檔案、設定預測天數（1-30 天）、為模型命名，系統自動建構 LSTM 模型、執行超參數調整並完成訓練
2. **使用已訓練模型進行預測**: 使用者選擇模型與預測起始日期，系統執行預測並以圖表顯示歷史股價與預測股價

### P2 優先級
3. **管理與匯入歷史股價資料**: 查看、上傳、刪除歷史股價 CSV 檔案

### P3 優先級
4. **比較多個模型的預測結果**: 同時選擇多個模型並排顯示預測圖表

## 開發工作流程

1. **查看規格**: 閱讀 `specs/001-stock-price-prediction/spec.md` 了解需求
2. **查看計畫**: 閱讀 `specs/001-stock-price-prediction/plan.md` 了解技術決策
3. **查看任務**: 閱讀 `specs/001-stock-price-prediction/tasks.md` 了解實作步驟
4. **實作順序**:
   - Phase 1: Setup (專案結構)
   - Phase 2: Foundational (核心基礎設施，**阻塞所有使用者故事**)
   - Phase 3-6: 按優先級實作使用者故事
   - Phase 7: Polish (橫切關注點)

## 資料驗證規則

### CSV 檔案驗證
- 必須包含必要欄位: date, open, high, low, close, volume
- 日期格式: YYYY/M/D 或 YYYY-MM-DD
- 價格必須 > 0，high >= low
- 至少 60 筆資料才能訓練模型
- 檔案大小限制: 100MB

### 預測請求驗證
- `startDate` 必須在資料檔案時間範圍內
- `startDate` 之前必須有足夠的歷史資料（至少 lookbackWindow 筆，預設 60 筆）
- 模型狀態必須為 `ready`
- 資料檔案狀態必須為 `valid`

## LSTM 模型架構

- **架構**: Sequential LSTM 神經網路
- **超參數調整**: 使用 Keras Tuner (Hyperband 演算法)
- **可調超參數**: lstmUnits1, lstmUnits2, dropout, learningRate, batchSize, epochs
- **固定參數**: lookbackWindow (預設 60)
- **輸入**: 過去 N 天的股價資料
- **輸出**: 未來 1-30 天的股價預測、漲跌機率、變化幅度

## 數據預處理 (Data Preprocessing)

### 特徵縮放 (Feature Scaling)
- **方法**: MinMaxScaler (0-1 正規化)
- **套件**: scikit-learn (`sklearn.preprocessing.MinMaxScaler`)
- **理由**: LSTM 使用 sigmoid/tanh 激活函數，對 0-1 範圍的數據效果較好
- **特徵欄位**: open, high, low, close, volume 及所有技術指標欄位
- **重要**: 訓練時的 scaler 參數必須與模型一起儲存，預測時使用相同的縮放參數

### 預處理流程
1. **特徵選擇**: 選取價格欄位與技術指標
2. **正規化**: 使用 MinMaxScaler 將所有特徵縮放至 [0, 1] 範圍
3. **時間序列視窗切割**: 根據 lookbackWindow 建立輸入序列 (預設 60 天)
4. **訓練/驗證集分割**: 80/20 分割比例
5. **反正規化**: 預測結果需進行 inverse_transform 轉換回原始股價尺度

### data_preprocessor.py 核心方法
- `preprocess_data()`: 完整預處理流程，回傳訓練/驗證資料
- `create_sequences()`: 建立時間序列視窗
- `inverse_transform()`: 將預測結果反正規化回原始股價尺度

## 除錯與日誌

- **訓練日誌**: `backend/logs/training.log` - 記錄訓練開始/完成時間、模型參數、評估指標
- **應用程式日誌**: `backend/logs/app.log` - 記錄錯誤與系統事件
- **元資料**: `backend/data/metadata.json` - 所有資料檔案、模型、訓練任務的元資料

## 重要注意事項

1. **前後端分離**: 後端與前端透過 RESTful API 通訊，後端需啟用 CORS (Flask-CORS)
2. **檔案命名**: 使用 UUID 前綴避免檔名衝突
3. **軟刪除**: 資料檔案與模型刪除時使用軟刪除（更新 status 為 deleted）
4. **原子操作**: 更新 metadata.json 使用臨時檔案 + 重新命名確保原子性
5. **進度監控**: 訓練任務支援進度輪詢，前端定期呼叫 API 查詢狀態
6. **錯誤處理**: 所有錯誤訊息必須使用正體中文，提供清楚的問題說明
7. **超參數調整**: 訓練時自動執行，無需手動配置
8. **GPU 自動偵測**: 系統啟動時自動偵測並配置可用的 GPU 裝置

## 常見開發問題

### 問題 1: 虛擬環境啟動失敗
**Windows**: 確認執行 `venv\Scripts\activate`（反斜線）
**macOS/Linux**: 確認執行 `source venv/bin/activate`（正斜線）

### 問題 2: 訓練速度過慢
- **CPU 模式**: 小資料集測試正常，大資料集建議使用 GPU
- **GPU 模式**: 參考 `WSL2-GPU-SETUP.md` 設定 GPU 加速
- **效能差異**: CPU 約 20-30 分鐘，GPU 約 4-6 分鐘（RTX 4070，7976 筆資料）

### 問題 3: CORS 錯誤
確認後端已啟用 CORS (Flask-CORS)，且前端呼叫的 URL 正確（`http://localhost:5000/api`）

### 問題 4: 找不到 metadata.json
首次啟動會自動建立 `backend/data/metadata.json`，確認 `backend/data/` 目錄存在

## 測試資料

- **範例 CSV**: `19940513-20251111-converted.csv` (台股歷史資料，1994-2025)
- **資料筆數**: 約 7890 筆
- **時間範圍**: 1994/5/13 - 2025/11/11
- **用途**: 用於開發測試、驗證系統功能

## 參考文件

- **功能規格**: `specs/001-stock-price-prediction/spec.md`
- **實作計畫**: `specs/001-stock-price-prediction/plan.md`
- **資料模型**: `specs/001-stock-price-prediction/data-model.md`
- **任務清單**: `specs/001-stock-price-prediction/tasks.md`
- **快速入門**: `specs/001-stock-price-prediction/quickstart.md`
- **API 合約**: `specs/001-stock-price-prediction/contracts/api.yaml`
- **專案憲章**: `.specify/memory/constitution.md`
