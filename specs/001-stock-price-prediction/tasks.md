---

description: "Task list for stock price prediction system implementation"
---

# Tasks: 股價漲跌機率預測系統

**Input**: Design documents from `/specs/001-stock-price-prediction/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api.yaml, research.md, quickstart.md

**Tests**: 本專案不包含測試任務（規格中未要求測試）

**Organization**: 任務依使用者故事（User Story）分組，確保每個故事可獨立實作與測試

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行執行（不同檔案、無依賴關係）
- **[Story]**: 此任務所屬的使用者故事（US1, US2, US3, US4）
- 所有任務包含精確的檔案路徑

## Path Conventions

- 前後端分離架構
- 後端：`backend/src/`
- 前端：`frontend/`
- 資料儲存：`backend/data/`
- 模型儲存：`backend/models/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 專案初始化與基本結構建立

- [X] T001 建立後端專案結構：建立 backend/src/ 目錄與子目錄（api/、models/、services/、ml/、utils/）
- [X] T002 建立前端專案結構：建立 frontend/ 目錄與子目錄（pages/、css/、js/、assets/）
- [X] T003 建立資料與模型儲存目錄：建立 backend/data/uploaded/、backend/models/、backend/logs/
- [X] T004 建立 backend/requirements.txt 並列出所有依賴套件（Flask 3.0.0、TensorFlow 2.15.0、Keras Tuner 1.4.6、pandas 2.1.4、Flask-CORS 4.0.0）
- [X] T005 [P] 建立 backend/.flake8 配置檔案（max-line-length = 88、extend-ignore = E203, W503）
- [X] T006 [P] 建立 backend/.gitignore 檔案（排除 venv/、__pycache__/、*.pyc、data/uploaded/、models/、logs/）
- [X] T007 [P] 建立專案根目錄 README.md 檔案（包含專案說明、技術堆疊、啟動指令）

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 核心基礎設施，必須完成後才能開始任何使用者故事實作

**⚠️ CRITICAL**: 所有使用者故事工作必須等待此階段完成

- [X] T008 建立 Flask 應用程式進入點 backend/src/app.py（包含 Flask 初始化、CORS 配置、API 路由註冊）
- [X] T009 建立配置管理模組 backend/src/config.py（包含資料路徑、模型路徑、日誌配置）
- [X] T010 建立元資料管理服務 backend/src/services/metadata_service.py（包含 JSON 讀寫、原子操作、CRUD 方法）
- [X] T011 建立檔案工具模組 backend/src/utils/file_utils.py（包含檔案命名、UUID 產生、檔案刪除）
- [X] T012 建立日期處理工具模組 backend/src/utils/date_utils.py（包含日期解析、格式轉換、範圍驗證）
- [X] T013 [P] 建立 CSV 驗證工具模組 backend/src/utils/csv_validator.py（包含必要欄位檢查、數值驗證、日期格式檢查）
- [X] T014 [P] 初始化 backend/data/metadata.json 檔案（包含 version、lastUpdated、dataFiles、models、trainingTasks 空陣列）
- [X] T015 [P] 建立前端 API 呼叫封裝模組 frontend/js/api.js（包含 Fetch API 封裝、錯誤處理、baseURL 配置）
- [X] T016 [P] 建立前端全域樣式 frontend/css/style.css（包含導航選單、按鈕、表單、卡片元件樣式）
- [X] T017 [P] 建立前端首頁 frontend/index.html（包含導航選單、功能入口連結：資料管理、模型訓練、預測執行、模型比較）

**Checkpoint**: 基礎設施就緒 - 使用者故事實作現在可以開始平行進行

---

## Phase 3: User Story 1 - 訓練股價預測模型 (Priority: P1) 🎯 MVP

**Goal**: 使用者能使用已匯入的資料檔案訓練 LSTM 模型，系統自動執行超參數調整並完成訓練

**Independent Test**: 選擇已匯入的資料檔案、設定預測天數為 5 天、輸入模型名稱，執行訓練流程，驗證系統能成功訓練模型並顯示評估指標

### Implementation for User Story 1

- [X] T018 [P] [US1] 建立資料檔案模型 backend/src/models/data_file.py（包含 DataFile、DateRange dataclass、to_dict/from_dict 方法）
- [X] T019 [P] [US1] 建立預測模型實體 backend/src/models/prediction_model.py（包含 PredictionModel、ModelMetrics dataclass、to_dict/from_dict 方法）
- [X] T020 [P] [US1] 建立訓練任務實體 backend/src/models/training_task.py（包含 TrainingTask dataclass、狀態管理）
- [X] T021 [US1] 建立 LSTM 模型建構器 backend/src/ml/model_builder.py（包含 build_lstm_model 函式、Sequential API、LSTM 層定義、Dropout、Dense 層）
- [X] T022 [US1] 建立超參數調整模組 backend/src/ml/hyperparameter_tuner.py（包含 Keras Tuner Hyperband 配置、build_model 函式、超參數搜索空間定義）
- [X] T023 [US1] 建立資料預處理模組 backend/src/ml/data_preprocessor.py（包含時間序列視窗切割、正規化、訓練/驗證集分割、lookback_window 邏輯）
- [X] T024 [US1] 建立模型訓練器 backend/src/ml/trainer.py（包含訓練流程、Keras Tuner 整合、模型儲存、進度回調）
- [X] T025 [US1] 建立模型服務 backend/src/services/model_service.py（包含模型 CRUD、載入模型、刪除模型邏輯）
- [X] T026 [US1] 建立訓練服務 backend/src/services/training_service.py（包含啟動訓練任務、監控進度、更新任務狀態、整合 metadata_service）
- [X] T027 [US1] 建立模型訓練 API 路由 backend/src/api/training_routes.py（包含 POST /api/models/train、GET /api/models/training/tasks/{taskId}、請求驗證、錯誤處理）
- [X] T028 [US1] 建立模型管理 API 路由 backend/src/api/model_routes.py（包含 GET /api/models、GET /api/models/{modelId}、DELETE /api/models/{modelId}、回應格式化）
- [X] T029 [US1] 建立前端模型訓練頁面 frontend/pages/model-training.html（包含資料檔案下拉選單、模型名稱輸入、預測天數輸入、開始訓練按鈕、進度顯示區域）
- [X] T030 [US1] 建立前端訓練邏輯模組 frontend/js/model-training.js（包含表單提交處理、API 呼叫、進度輪詢、結果顯示、錯誤處理）

**Checkpoint**: User Story 1 完成 - 模型訓練功能可獨立測試並交付價值

---

## Phase 4: User Story 2 - 使用已訓練模型進行股價預測 (Priority: P1) 🎯 MVP

**Goal**: 使用者能選擇已訓練模型與預測起始日期，執行預測並以圖表顯示歷史股價與預測股價

**Independent Test**: 選擇已訓練模型、選擇資料檔案、指定預測起始日期（如 2025-10-01），驗證系統顯示預測結果與視覺化圖表

### Implementation for User Story 2

- [ ] T031 [P] [US2] 建立預測請求模型 backend/src/models/prediction.py（包含 PredictionRequest、PredictionResult、HistoricalDataPoint、PredictionDataPoint dataclass）
- [ ] T032 [US2] 建立模型預測器 backend/src/ml/predictor.py（包含載入模型、資料預處理、執行預測、機率計算、預測股價計算邏輯）
- [ ] T033 [US2] 建立預測服務 backend/src/services/prediction_service.py（包含驗證預測請求、載入歷史資料、執行預測、格式化結果、整合 metadata_service）
- [ ] T034 [US2] 建立預測執行 API 路由 backend/src/api/prediction_routes.py（包含 POST /api/predict、請求驗證、日期範圍檢查、資料充足性驗證、錯誤訊息）
- [ ] T035 [US2] 建立前端圖表渲染模組 frontend/js/chart-renderer.js（包含 Chart.js 配置、雙資料集折線圖、歷史股價藍色實線、預測股價紅色虛線、互動功能：懸停、縮放、平移）
- [ ] T036 [US2] 建立前端預測頁面 frontend/pages/prediction.html（包含模型下拉選單、資料檔案下拉選單、預測起始日期選擇器（HTML5 date input）、開始預測按鈕、圖表容器）
- [ ] T037 [US2] 建立前端預測邏輯模組 frontend/js/prediction.js（包含表單處理、API 呼叫、預測結果處理、圖表渲染呼叫、錯誤提示）

**Checkpoint**: User Story 1 和 2 完成 - MVP 核心功能（訓練與預測）可獨立運作並交付

---

## Phase 5: User Story 3 - 管理與匯入歷史股價資料 (Priority: P2)

**Goal**: 使用者能查看、上傳、刪除歷史股價資料 CSV 檔案

**Independent Test**: 查看資料清單、上傳符合格式的 CSV 檔案（如 19940513-20251111-converted.csv），驗證系統成功載入並顯示資料

### Implementation for User Story 3

- [ ] T038 [P] [US3] 建立資料服務 backend/src/services/data_service.py（包含上傳檔案處理、CSV 解析、驗證邏輯、儲存檔案、更新 metadata.json、列出資料檔案、刪除檔案）
- [ ] T039 [US3] 建立資料管理 API 路由 backend/src/api/data_routes.py（包含 POST /api/data/upload、GET /api/data/files、DELETE /api/data/files/{fileId}、multipart/form-data 處理、錯誤回應）
- [ ] T040 [US3] 建立前端資料管理頁面 frontend/pages/data-management.html（包含資料清單表格、匯入資料按鈕、檔案上傳表單、檔案名稱輸入、刪除按鈕）
- [ ] T041 [US3] 建立前端資料管理邏輯模組 frontend/js/data-management.js（包含載入資料清單、上傳檔案處理、FormData 建立、刪除資料檔案、更新列表）

**Checkpoint**: User Stories 1-3 完成 - 資料管理功能獨立運作

---

## Phase 6: User Story 4 - 比較多個模型的預測結果 (Priority: P3)

**Goal**: 使用者能同時選擇多個模型，並排顯示預測結果圖表進行比較

**Independent Test**: 選擇 2-3 個模型、選擇相同資料檔案與預測起始日期，驗證系統並排顯示不同模型的預測圖表

### Implementation for User Story 4

- [ ] T042 [US4] 擴展預測服務 backend/src/services/prediction_service.py（新增 compare_models 方法、批次執行預測、彙整多模型結果）
- [ ] T043 [US4] 擴展預測 API 路由 backend/src/api/prediction_routes.py（新增 POST /api/predict/compare、modelIds 陣列驗證、回應格式）
- [ ] T044 [US4] 建立前端模型比較頁面 frontend/pages/model-comparison.html（包含多選模型列表、資料檔案選擇、預測起始日期選擇、開始比較按鈕、並排圖表容器）
- [ ] T045 [US4] 擴展前端圖表渲染模組 frontend/js/chart-renderer.js（新增 renderComparisonCharts 函式、並排佈局、多圖表渲染）
- [ ] T046 [US4] 建立前端比較邏輯模組 frontend/js/model-comparison.js（包含多選處理、批次 API 呼叫、並排圖表渲染、互動功能）

**Checkpoint**: 所有使用者故事完成 - 系統功能完整

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 改進影響多個使用者故事的橫切關注點

- [ ] T047 [P] 建立前端工具模組 frontend/js/utils.js（包含日期格式化、錯誤提示、載入中狀態顯示、表單驗證輔助函式）
- [ ] T048 [P] 建立前端元件樣式 frontend/css/components.css（包含卡片、進度條、錯誤提示、成功提示、表格樣式）
- [ ] T049 [P] 新增錯誤日誌記錄至 backend/src/utils/logger.py（包含 Python logging 配置、寫入 backend/logs/app.log）
- [ ] T050 [P] 新增訓練日誌記錄至 backend/logs/training.log（包含訓練開始/完成時間、模型參數、評估指標）
- [ ] T051 更新 backend/src/app.py 註冊所有 API 路由（包含 data_routes、model_routes、training_routes、prediction_routes）
- [ ] T052 更新 frontend/index.html 完善導航選單連結（確保所有頁面可導航）
- [ ] T053 [P] 新增邊界情況錯誤處理：資料不足（< 60 筆）、CSV 格式錯誤、檔案過大（> 100MB）、預測日期無效、儲存空間不足
- [ ] T054 [P] 新增使用者友善的正體中文錯誤訊息至所有 API 端點
- [ ] T055 執行 quickstart.md 驗證流程（上傳範例 CSV、訓練模型、執行預測、確認所有功能正常運作）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 無依賴 - 可立即開始
- **Foundational (Phase 2)**: 依賴 Setup 完成 - **阻塞所有使用者故事**
- **User Stories (Phases 3-6)**: 全部依賴 Foundational 完成
  - User Story 1 (P1): Foundational 完成後可開始 - 無其他故事依賴
  - User Story 2 (P1): 依賴 Foundational - 無其他故事依賴（獨立測試）
  - User Story 3 (P2): 依賴 Foundational - 無其他故事依賴（獨立測試）
  - User Story 4 (P3): 依賴 Foundational - 可與 US2 整合但應獨立測試
- **Polish (Phase 7)**: 依賴所有期望的使用者故事完成

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 完成後可開始 - 獨立可測試
- **User Story 2 (P1)**: Foundational 完成後可開始 - 獨立可測試（需要 US1 產生的模型進行完整測試）
- **User Story 3 (P2)**: Foundational 完成後可開始 - 完全獨立可測試
- **User Story 4 (P3)**: Foundational 完成後可開始 - 需要 US1 和 US2 的模型與預測功能進行整合測試

### Within Each User Story

- 模型（dataclass）先於服務
- 服務先於 API 路由
- 核心實作先於整合
- 完成故事再移至下一優先級

### Parallel Opportunities

- **Setup phase**: T005、T006、T007 可平行執行
- **Foundational phase**: T013、T014、T015、T016、T017 可平行執行
- **User Story 1**: T018、T019、T020 可平行執行（不同檔案、無依賴）
- **User Story 2**: T031 可與 US1 任務平行執行
- **User Story 3**: T038 可與 US1/US2 任務平行執行（不同檔案）
- **Polish phase**: T047、T048、T049、T050、T053、T054 可平行執行

**多人團隊策略**: Foundational 完成後，可將 US1、US2、US3 分配給不同開發者平行實作

---

## Parallel Example: User Story 1

```bash
# 同時啟動 User Story 1 的模型建立任務：
Task: "建立資料檔案模型 backend/src/models/data_file.py"
Task: "建立預測模型實體 backend/src/models/prediction_model.py"
Task: "建立訓練任務實體 backend/src/models/training_task.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（**CRITICAL** - 阻塞所有故事）
3. 完成 Phase 3: User Story 1（模型訓練）
4. **STOP and VALIDATE**: 獨立測試 User Story 1
5. 完成 Phase 4: User Story 2（預測執行）
6. **STOP and VALIDATE**: 獨立測試 User Story 2
7. 部署/演示 MVP

### Incremental Delivery

1. Setup + Foundational → 基礎就緒
2. 新增 User Story 1 → 獨立測試 → 部署/演示（MVP 核心！）
3. 新增 User Story 2 → 獨立測試 → 部署/演示（MVP 完整！）
4. 新增 User Story 3 → 獨立測試 → 部署/演示
5. 新增 User Story 4 → 獨立測試 → 部署/演示
6. 每個故事都增加價值且不破壞先前功能

### Parallel Team Strategy

多人開發團隊：

1. 團隊共同完成 Setup + Foundational
2. Foundational 完成後：
   - 開發者 A: User Story 1（模型訓練）
   - 開發者 B: User Story 2（預測執行）
   - 開發者 C: User Story 3（資料管理）
3. 各故事獨立完成與整合

---

## Notes

- **[P] 任務** = 不同檔案、無依賴關係
- **[Story] 標籤** 將任務映射至特定使用者故事以利追蹤
- 每個使用者故事應可獨立完成與測試
- 在檢查點停止以獨立驗證故事功能
- 每個任務或邏輯組合後提交 Git
- **避免**: 模糊任務、相同檔案衝突、破壞獨立性的跨故事依賴
- **技術堆疊**: Python 3.11+、Flask 3.0.0、TensorFlow 2.15.0、原生 JavaScript ES6+、Chart.js 4.4.0
- **儲存方案**: 檔案系統 + JSON 元資料（backend/data/metadata.json）
- **API 命名**: camelCase（符合憲章要求）
- **所有文字**: 正體中文（符合憲章要求）

---

## Task Summary

| Phase | Task Count | Description |
|-------|-----------|-------------|
| Phase 1: Setup | 7 | 專案結構與配置 |
| Phase 2: Foundational | 10 | 核心基礎設施（阻塞所有故事）|
| Phase 3: User Story 1 (P1) 🎯 | 13 | 模型訓練功能 |
| Phase 4: User Story 2 (P1) 🎯 | 7 | 預測執行與視覺化 |
| Phase 5: User Story 3 (P2) | 4 | 資料管理功能 |
| Phase 6: User Story 4 (P3) | 5 | 模型比較功能 |
| Phase 7: Polish | 9 | 橫切關注點與優化 |
| **Total** | **55** | **完整系統實作** |

**MVP Scope (建議)**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) = **37 tasks**

**Parallel Opportunities**: 20+ tasks 標記為 [P]，可平行執行以加速開發

**Independent Test Criteria**:
- US1: 上傳 CSV → 訓練模型 → 查看評估指標
- US2: 選擇模型 → 選擇日期 → 查看預測圖表
- US3: 上傳 CSV → 查看清單 → 刪除檔案
- US4: 選擇多模型 → 查看並排圖表

---

**版本**: 1.0.0
**產生日期**: 2025-11-13
**基於**: spec.md (P1-P3 stories), plan.md (Flask + TensorFlow + 原生 JS), data-model.md (8 entities), contracts/api.yaml (11 endpoints)
