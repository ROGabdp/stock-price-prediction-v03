# Implementation Plan: 股價漲跌機率預測系統

**Branch**: `001-stock-price-prediction` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-stock-price-prediction/spec.md`

## Summary

開發一個股價漲跌機率預測系統，使用 LSTM 神經網路從歷史資料中學習，預測未來 1-30 天的股價漲跌機率與幅度。系統採用 **Flask + TensorFlow/Keras** 後端，**原生 JavaScript + Chart.js** 前端，**檔案系統** 儲存，遵循「簡潔務實」與「嚴格禁止過度設計」原則，專注於 MVP 核心功能（P1 故事：模型訓練與預測）。

**技術方案**：
- 後端：Flask（輕量 Web 框架）+ TensorFlow/Keras（LSTM 模型）+ Keras Tuner（超參數調整）
- 前端：原生 JavaScript（避免框架複雜性）+ Chart.js（圖表視覺化）
- 儲存：檔案系統 + JSON 元資料（避免資料庫過度設計）
- 架構：前後端分離 RESTful API

---

## Technical Context

**Language/Version**: Python 3.11+, JavaScript ES6+  
**Primary Dependencies**: Flask 3.0.0, TensorFlow 2.15.0, Keras Tuner 1.4.6, pandas 2.1.4, Chart.js 4.4.0 (CDN)  
**Storage**: 檔案系統（CSV 資料 + JSON 元資料 + .keras 模型檔案）  
**Testing**: pytest（後端，選填）  
**Target Platform**: Windows/macOS/Linux 桌面瀏覽器（Chrome、Firefox、Edge）  
**Project Type**: web（前後端分離）  
**Performance Goals**: 
- 模型訓練時間：中等資料量（250 筆/年）約 3-10 分鐘
- 預測回應時間：< 5 秒
- 圖表載入時間：< 5 秒（1000 個資料點以內）  
**Constraints**: 
- 單機環境，無分散式需求
- 小規模使用者（< 10 人）
- 檔案大小限制：100MB
- 記憶體：至少 8GB RAM  
**Scale/Scope**: 
- 50 個訓練模型
- 100 個資料檔案
- 每個資料檔案約 1000-10000 筆歷史資料

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 憲章合規性檢查

| 憲章原則 | 檢查結果 | 說明 |
|----------|---------|------|
| **I. 正體中文優先** | ✅ 通過 | 所有文件（spec.md、plan.md、research.md、data-model.md、quickstart.md）、程式碼註解、UI 文字、錯誤訊息、API 回應訊息皆使用正體中文 |
| **II. 規格驅動開發** | ✅ 通過 | 所有技術決策基於 spec.md 的 User Stories、Functional Requirements、Key Entities；資料模型直接對應 Key Entities；API 設計涵蓋所有 FR |
| **III. 高品質可測試的 MVP** | ✅ 通過 | 專注 P1 故事（User Story 1: 訓練模型、User Story 2: 執行預測）；每個功能具備明確驗收標準；API 端點可獨立測試 |
| **IV. 嚴格禁止過度設計** | ✅ 通過 | 選擇最簡單方案：原生 JavaScript（非 Vue/React）、檔案系統（非資料庫）、Flask（非 Django）、HTML5 原生元件（非第三方函式庫）；無預測性設計 |
| **V. Pythonic 與 PEP 8** | ✅ 通過 | 使用 dataclass、型別提示、snake_case 命名；配置 black + flake8 自動格式化與檢查 |
| **VI. Idiomatic JavaScript** | ✅ 通過 | 使用 ES6+ 語法（async/await、箭頭函式、解構）、camelCase 命名、Fetch API（原生）；配置 ESLint + Prettier |
| **VII. 簡潔務實** | ✅ 通過 | 優先使用成熟函式庫（pandas、Chart.js、Keras Tuner）；避免自行實作已有解決方案的功能；程式碼保持簡短與單一職責 |

**結論**: ✅ 所有憲章原則皆已通過，無違規項目，無需填寫「複雜性追蹤」表格。

---

## Project Structure

### Documentation (this feature)

```text
specs/001-stock-price-prediction/
├── spec.md              # 功能規格（User Stories、FR、Entities）
├── plan.md              # 本檔案（實作計畫）
├── research.md          # 技術研究與決策（Phase 0）
├── data-model.md        # 資料模型設計（Phase 1）
├── quickstart.md        # 快速入門指南（Phase 1）
├── contracts/           # API 合約（Phase 1）
│   └── api.yaml         # OpenAPI 3.0 規格
└── tasks.md             # 任務清單（Phase 2，由 /speckit.tasks 產生）
```

### Source Code (repository root)

```text
stock-price-prediction-v03/
├── backend/                              # 後端專案根目錄
│   ├── src/                              # 後端原始碼
│   │   ├── app.py                        # Flask 應用程式進入點
│   │   ├── config.py                     # 配置管理
│   │   ├── api/                          # API 路由層
│   │   │   ├── __init__.py
│   │   │   ├── data_routes.py           # 資料管理 API (/api/data/*)
│   │   │   ├── model_routes.py          # 模型管理 API (/api/models/*)
│   │   │   ├── training_routes.py       # 模型訓練 API (/api/models/train)
│   │   │   └── prediction_routes.py     # 預測執行 API (/api/predict)
│   │   ├── models/                       # 資料模型層（dataclass）
│   │   │   ├── __init__.py
│   │   │   ├── data_file.py             # DataFile 模型
│   │   │   ├── prediction_model.py      # PredictionModel 模型
│   │   │   ├── training_task.py         # TrainingTask 模型
│   │   │   └── prediction.py            # PredictionRequest/Result 模型
│   │   ├── services/                     # 業務邏輯層
│   │   │   ├── __init__.py
│   │   │   ├── metadata_service.py      # 元資料管理服務（CRUD）
│   │   │   ├── data_service.py          # 資料檔案服務（上傳、驗證）
│   │   │   ├── training_service.py      # 訓練服務（啟動訓練、監控進度）
│   │   │   └── prediction_service.py    # 預測服務（執行預測、產生結果）
│   │   ├── ml/                           # 機器學習模組
│   │   │   ├── __init__.py
│   │   │   ├── model_builder.py         # LSTM 模型建構器
│   │   │   ├── hyperparameter_tuner.py  # Keras Tuner 超參數調整
│   │   │   ├── trainer.py               # 模型訓練邏輯
│   │   │   └── predictor.py             # 模型預測邏輯
│   │   └── utils/                        # 工具函式
│   │       ├── __init__.py
│   │       ├── csv_validator.py         # CSV 驗證工具
│   │       ├── date_utils.py            # 日期處理工具
│   │       └── file_utils.py            # 檔案操作工具
│   ├── data/                             # 資料儲存目錄
│   │   ├── uploaded/                     # 上傳的 CSV 檔案
│   │   └── metadata.json                 # 元資料檔案
│   ├── models/                           # 訓練模型儲存目錄
│   ├── logs/                             # 日誌目錄
│   │   └── training.log
│   ├── tests/                            # 測試（選填）
│   │   ├── test_data_service.py
│   │   ├── test_training_service.py
│   │   └── test_prediction_service.py
│   ├── requirements.txt                  # Python 依賴清單
│   ├── .flake8                           # flake8 配置
│   └── README.md                         # 後端說明文件
│
├── frontend/                             # 前端專案根目錄
│   ├── index.html                        # 首頁（導航選單）
│   ├── pages/                            # 各功能頁面
│   │   ├── data-management.html         # 資料管理頁面
│   │   ├── model-training.html          # 模型訓練頁面
│   │   ├── prediction.html              # 預測執行頁面
│   │   └── model-comparison.html        # 模型比較頁面（P3）
│   ├── css/                              # 樣式檔案
│   │   ├── style.css                    # 全域樣式
│   │   └── components.css               # 元件樣式
│   ├── js/                               # JavaScript 模組
│   │   ├── api.js                       # API 呼叫封裝（Fetch API）
│   │   ├── data-management.js           # 資料管理邏輯
│   │   ├── model-training.js            # 模型訓練邏輯
│   │   ├── prediction.js                # 預測執行邏輯
│   │   ├── chart-renderer.js            # Chart.js 圖表渲染
│   │   └── utils.js                     # 工具函式（日期格式化、錯誤處理）
│   └── assets/                           # 靜態資源
│       └── images/
│
├── .gitignore                            # Git 忽略檔案清單
├── README.md                             # 專案說明文件
└── specs/                                # 規格文件目錄（上述 Documentation 部分）
```

**結構決策說明**：

1. **前後端分離**: 
   - `backend/` 與 `frontend/` 完全獨立，透過 RESTful API 通訊
   - 職責清晰：後端專注業務邏輯與 ML，前端專注 UI 與互動
   - 開發便利：可平行開發，前端修改無需重啟後端

2. **後端分層架構**:
   - **API 層** (`api/`): 處理 HTTP 請求/回應，路由定義
   - **業務邏輯層** (`services/`): 核心業務邏輯，與 API 層解耦
   - **資料模型層** (`models/`): dataclass 定義，資料結構與驗證
   - **ML 模組** (`ml/`): 機器學習專屬邏輯，獨立於業務邏輯
   - **工具層** (`utils/`): 可重用的工具函式

3. **前端模組化**:
   - 頁面分離：每個功能獨立 HTML 頁面，避免 SPA 複雜性
   - JavaScript 模組化：按功能拆分 JS 檔案，提高可維護性
   - CSS 分離：全域樣式與元件樣式分離

4. **儲存結構**:
   - `data/uploaded/`: CSV 檔案（命名：`file_{uuid}_{name}.csv`）
   - `data/metadata.json`: 集中式元資料（DataFile、Model、Task）
   - `models/`: 訓練模型（命名：`model_{id}_{name}.keras`）

---

## Complexity Tracking

> **本專案無憲章違規項目，此表格留空。**

---

**核准狀態**: 待審查  
**下一步**: 執行 `/speckit.tasks` 命令產生任務清單 (tasks.md)

---

**版本**: 1.0.0  
**最後更新**: 2025-11-13
