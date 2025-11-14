# 資料模型設計

**功能**: 股價漲跌機率預測系統  
**分支**: `001-stock-price-prediction`  
**日期**: 2025-11-13

## 執行摘要

本文件定義股價預測系統的資料模型，基於規格文件中的 Key Entities 設計。根據技術研究決策，採用**檔案系統 + JSON 元資料**方案，避免資料庫過度設計。

**核心實體**：
1. 資料檔案 (DataFile) - CSV 歷史股價資料
2. 歷史股價資料 (HistoricalStockData) - CSV 內的股價記錄
3. 預測模型 (PredictionModel) - 訓練好的 LSTM 模型
4. 預測請求 (PredictionRequest) - 使用者發起的預測請求
5. 預測結果 (PredictionResult) - 模型預測輸出
6. 訓練任務 (TrainingTask) - 模型訓練執行記錄
7. 超參數配置 (HyperparameterConfiguration) - 模型超參數設定
8. CSV 欄位定義 (CSVColumnDefinition) - CSV 格式規範

---

## 一、儲存方案架構

### 1.1 儲存結構總覽

```
backend/
├── data/
│   ├── uploaded/                        # 上傳的 CSV 檔案
│   │   ├── file_a3f2b1c4_台股歷史資料.csv
│   │   └── file_d8e7f6a5_美股資料.csv
│   └── metadata.json                    # 資料檔案與模型元資料（集中管理）
├── models/                              # 訓練好的模型
│   ├── model_001_台股預測v1.keras
│   └── model_002_台股預測v2.keras
└── logs/
    └── training.log                     # 訓練日誌

```

**設計理念**：
- **集中式元資料**: 所有元資料集中於 `metadata.json`，便於查詢與管理
- **檔案命名**: 使用 UUID 前綴確保唯一性，保留原檔名便於識別
- **原子操作**: 更新 `metadata.json` 時先寫入臨時檔案，再重新命名

---

### 1.2 metadata.json 結構

```json
{
  "version": "1.0",
  "lastUpdated": "2025-11-13T22:30:00",
  "dataFiles": [
    { /* DataFile 物件陣列，詳見 2.1 */ }
  ],
  "models": [
    { /* PredictionModel 物件陣列，詳見 2.3 */ }
  ],
  "trainingTasks": [
    { /* TrainingTask 物件陣列，詳見 2.6 */ }
  ]
}
```

**版本控制**：
- `version`: 元資料格式版本，用於未來遷移
- `lastUpdated`: 最後更新時間戳記

---

## 二、實體定義

### 2.1 資料檔案 (DataFile)

**描述**: 使用者上傳的 CSV 歷史股價資料檔案。

**儲存方式**: CSV 檔案 + JSON 元資料

**JSON 結構**：
```json
{
  "fileId": "file_a3f2b1c4",
  "fileName": "台股歷史資料.csv",
  "originalFileName": "19940513-20251111-converted.csv",
  "filePath": "data/uploaded/file_a3f2b1c4_台股歷史資料.csv",
  "uploadedAt": "2025-11-13T22:00:00",
  "dateRange": {
    "start": "1994-05-13",
    "end": "2025-11-11"
  },
  "rowCount": 7890,
  "columns": ["date", "open", "high", "low", "close", "volume", "SMA5", "SMA10", ...],
  "fileSizeBytes": 1048576,
  "status": "valid",
  "validationErrors": []
}
```

**欄位說明**：

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `fileId` | String | 必填、唯一 | UUID，檔案唯一識別符 |
| `fileName` | String | 必填 | 使用者自訂的檔案名稱（可編輯） |
| `originalFileName` | String | 必填 | 上傳時的原始檔案名稱 |
| `filePath` | String | 必填 | 檔案系統路徑（相對於 backend/ 目錄） |
| `uploadedAt` | String (ISO 8601) | 必填 | 上傳時間 |
| `dateRange.start` | String (YYYY-MM-DD) | 必填 | 資料起始日期 |
| `dateRange.end` | String (YYYY-MM-DD) | 必填 | 資料結束日期 |
| `rowCount` | Integer | 必填 | 資料筆數（不含標題列） |
| `columns` | Array<String> | 必填 | CSV 欄位名稱列表 |
| `fileSizeBytes` | Integer | 必填 | 檔案大小（位元組） |
| `status` | String | 必填 | 狀態：`valid`, `invalid`, `deleted` |
| `validationErrors` | Array<String> | 選填 | 驗證錯誤訊息列表 |

**驗證規則**：
1. **必要欄位檢查**: 必須包含 `date`, `open`, `high`, `low`, `close`, `volume`
2. **日期格式驗證**: `date` 欄位必須為 `YYYY/M/D` 或 `YYYY-MM-DD` 格式
3. **數值有效性**: 價格與成交量必須為正數
4. **資料量檢查**: 至少 60 筆資料
5. **檔案大小限制**: 最多 100MB
6. **重複日期檢查**: 同一日期不可重複

**狀態轉換**：
```
[上傳] → valid (驗證通過)
       → invalid (驗證失敗)
[刪除] → deleted (軟刪除，保留元資料)
```

**範例 Python 類別**（用於驗證與操作）：
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class DateRange:
    start: str  # YYYY-MM-DD
    end: str

@dataclass
class DataFile:
    file_id: str
    file_name: str
    original_file_name: str
    file_path: str
    uploaded_at: str  # ISO 8601
    date_range: DateRange
    row_count: int
    columns: List[str]
    file_size_bytes: int
    status: str  # valid, invalid, deleted
    validation_errors: List[str] = None
    
    def to_dict(self) -> dict:
        """轉換為 JSON 可序列化的字典"""
        return {
            "fileId": self.file_id,
            "fileName": self.file_name,
            "originalFileName": self.original_file_name,
            "filePath": self.file_path,
            "uploadedAt": self.uploaded_at,
            "dateRange": {
                "start": self.date_range.start,
                "end": self.date_range.end
            },
            "rowCount": self.row_count,
            "columns": self.columns,
            "fileSizeBytes": self.file_size_bytes,
            "status": self.status,
            "validationErrors": self.validation_errors or []
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DataFile':
        """從 JSON 字典建立物件"""
        return cls(
            file_id=data["fileId"],
            file_name=data["fileName"],
            original_file_name=data["originalFileName"],
            file_path=data["filePath"],
            uploaded_at=data["uploadedAt"],
            date_range=DateRange(
                start=data["dateRange"]["start"],
                end=data["dateRange"]["end"]
            ),
            row_count=data["rowCount"],
            columns=data["columns"],
            file_size_bytes=data["fileSizeBytes"],
            status=data["status"],
            validation_errors=data.get("validationErrors", [])
        )
```

---

### 2.2 歷史股價資料 (HistoricalStockData)

**描述**: CSV 檔案中的股價記錄，每筆代表一個交易日。

**儲存方式**: CSV 檔案內容（不存於 metadata.json）

**CSV 欄位定義**（基於範例檔案）：

| 欄位名稱 | 型別 | 必填 | 說明 |
|----------|------|------|------|
| `date` | Date | ✅ | 交易日期（YYYY/M/D 或 YYYY-MM-DD） |
| `open` | Float | ✅ | 開盤價 |
| `high` | Float | ✅ | 最高價 |
| `low` | Float | ✅ | 最低價 |
| `close` | Float | ✅ | 收盤價 |
| `volume` | Float | ✅ | 成交量（單位：億） |
| `SMA5` | Float | ❌ | 5 日簡單移動平均 |
| `SMA10` | Float | ❌ | 10 日簡單移動平均 |
| `SMA20` | Float | ❌ | 20 日簡單移動平均 |
| `SMA60` | Float | ❌ | 60 日簡單移動平均 |
| `SMA120` | Float | ❌ | 120 日簡單移動平均 |
| `SMA240` | Float | ❌ | 240 日簡單移動平均 |
| `MA5` | Float | ❌ | 5 日移動平均（成交量） |
| `MA10` | Float | ❌ | 10 日移動平均（成交量） |
| `DIF12-26` | Float | ❌ | MACD 指標 DIF |
| `MACD9` | Float | ❌ | MACD 指標 MACD |
| `OSC` | Float | ❌ | MACD 指標柱狀圖 |
| `K(9,3)` | Float | ❌ | KD 指標 K 值 |
| `D(9,3)` | Float | ❌ | KD 指標 D 值 |
| `net buy sell` | Float | ❌ | 三大法人買賣超 |
| `cumulative net buy sell` | Float | ❌ | 累積買賣超 |
| `buy` | Float | ❌ | 買入量 |
| `sell` | Float | ❌ | 賣出量 |

**資料驗證規則**：
1. `date` 必須可解析為有效日期
2. `open`, `high`, `low`, `close` 必須 > 0
3. `high` >= `low`
4. `volume` >= 0
5. 可選欄位若存在，必須為有效數值或空值

**範例 pandas DataFrame 操作**：
```python
import pandas as pd

def load_historical_data(file_path: str) -> pd.DataFrame:
    """載入歷史股價資料"""
    df = pd.read_csv(file_path, parse_dates=['date'])
    df = df.sort_values('date')
    
    # 驗證必要欄位
    required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要欄位：{', '.join(missing_cols)}")
    
    # 驗證數值有效性
    if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
        raise ValueError("價格欄位包含非正數值")
    
    if (df['high'] < df['low']).any():
        raise ValueError("最高價不可低於最低價")
    
    return df

def get_data_before_date(df: pd.DataFrame, before_date: str) -> pd.DataFrame:
    """取得指定日期之前的歷史資料"""
    return df[df['date'] < before_date]
```


---

### 2.3 預測模型 (PredictionModel)

**描述**: 訓練好的 LSTM 神經網路模型。

**儲存方式**: `.keras` 檔案 + JSON 元資料

**JSON 結構**：
```json
{
  "modelId": "model_001",
  "modelName": "台股預測 v1",
  "modelPath": "models/model_001_台股預測v1.keras",
  "trainedAt": "2025-11-13T22:30:00",
  "trainingDuration": 1200.5,
  "dataFileId": "file_a3f2b1c4",
  "dataFileName": "台股歷史資料.csv",
  "predictionDays": 5,
  "metrics": {
    "trainLoss": 0.05,
    "valLoss": 0.08,
    "trainMAE": 120.5,
    "valMAE": 150.2
  },
  "hyperparameters": {
    "lstmUnits1": 64,
    "lstmUnits2": 32,
    "dropout": 0.2,
    "learningRate": 0.001,
    "batchSize": 32,
    "epochs": 50,
    "lookbackWindow": 60
  },
  "trainingTaskId": "task_001",
  "status": "ready",
  "notes": ""
}
```

**欄位說明**：

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `modelId` | String | 必填、唯一 | 模型唯一識別符（格式：`model_XXX`） |
| `modelName` | String | 必填 | 使用者自訂的模型名稱 |
| `modelPath` | String | 必填 | 模型檔案路徑 |
| `trainedAt` | String (ISO 8601) | 必填 | 訓練完成時間 |
| `trainingDuration` | Float | 必填 | 訓練耗時（秒） |
| `dataFileId` | String | 必填 | 訓練使用的資料檔案 ID |
| `dataFileName` | String | 必填 | 資料檔案名稱（冗余欄位，便於顯示） |
| `predictionDays` | Integer | 必填 | 預測天數（1-30） |
| `metrics.trainLoss` | Float | 必填 | 訓練損失 |
| `metrics.valLoss` | Float | 必填 | 驗證損失 |
| `metrics.trainMAE` | Float | 必填 | 訓練平均絕對誤差 |
| `metrics.valMAE` | Float | 必填 | 驗證平均絕對誤差 |
| `hyperparameters.*` | Various | 必填 | 超參數配置（詳見 2.7） |
| `trainingTaskId` | String | 必填 | 關聯的訓練任務 ID |
| `status` | String | 必填 | 狀態：`ready`, `deleted` |
| `notes` | String | 選填 | 備註 |

**狀態**：
- `ready`: 模型可用於預測
- `deleted`: 已刪除（軟刪除）

**索引策略**（若未來遷移至資料庫）：
- 主鍵：`modelId`
- 索引：`dataFileId`（查詢某資料檔案訓練的所有模型）
- 索引：`trainedAt`（按訓練時間排序）

**範例 Python 類別**：
```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelMetrics:
    train_loss: float
    val_loss: float
    train_mae: float
    val_mae: float

@dataclass
class PredictionModel:
    model_id: str
    model_name: str
    model_path: str
    trained_at: str
    training_duration: float
    data_file_id: str
    data_file_name: str
    prediction_days: int
    metrics: ModelMetrics
    hyperparameters: Dict[str, any]
    training_task_id: str
    status: str
    notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "modelId": self.model_id,
            "modelName": self.model_name,
            "modelPath": self.model_path,
            "trainedAt": self.trained_at,
            "trainingDuration": self.training_duration,
            "dataFileId": self.data_file_id,
            "dataFileName": self.data_file_name,
            "predictionDays": self.prediction_days,
            "metrics": {
                "trainLoss": self.metrics.train_loss,
                "valLoss": self.metrics.val_loss,
                "trainMAE": self.metrics.train_mae,
                "valMAE": self.metrics.val_mae
            },
            "hyperparameters": self.hyperparameters,
            "trainingTaskId": self.training_task_id,
            "status": self.status,
            "notes": self.notes
        }
```

---

### 2.4 預測請求 (PredictionRequest)

**描述**: 使用者發起的預測請求（暫態實體，不持久化儲存）。

**用途**: API 請求物件，驗證與傳遞參數。

**JSON 結構**（API 請求 Body）：
```json
{
  "modelId": "model_001",
  "dataFileId": "file_a3f2b1c4",
  "startDate": "2025-10-01"
}
```

**欄位說明**：

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `modelId` | String | 必填 | 要使用的模型 ID |
| `dataFileId` | String | 必填 | 資料檔案 ID |
| `startDate` | String (YYYY-MM-DD) | 必填 | 預測起始日期 |

**驗證規則**：
1. `modelId` 必須存在且狀態為 `ready`
2. `dataFileId` 必須存在且狀態為 `valid`
3. `startDate` 必須在資料檔案的時間範圍內
4. `startDate` 之前的資料筆數必須 >= 模型的 `lookbackWindow`（預設 60 筆）

**範例 Python 類別**：
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PredictionRequest:
    model_id: str
    data_file_id: str
    start_date: str  # YYYY-MM-DD
    
    def validate(self, model: PredictionModel, data_file: DataFile) -> List[str]:
        """驗證請求參數，回傳錯誤訊息列表"""
        errors = []
        
        # 驗證模型狀態
        if model.status != 'ready':
            errors.append("模型不可用")
        
        # 驗證資料檔案狀態
        if data_file.status != 'valid':
            errors.append("資料檔案不可用")
        
        # 驗證日期範圍
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        file_start = datetime.strptime(data_file.date_range.start, '%Y-%m-%d').date()
        file_end = datetime.strptime(data_file.date_range.end, '%Y-%m-%d').date()
        
        if start_date < file_start or start_date > file_end:
            errors.append(f"預測起始日期必須在資料範圍內（{data_file.date_range.start} 至 {data_file.date_range.end}）")
        
        return errors
```

---

### 2.5 預測結果 (PredictionResult)

**描述**: 模型針對特定請求產生的預測輸出（暫態實體，不持久化儲存）。

**用途**: API 回應物件，回傳給前端顯示。

**JSON 結構**（API 回應）：
```json
{
  "requestInfo": {
    "modelId": "model_001",
    "modelName": "台股預測 v1",
    "dataFileId": "file_a3f2b1c4",
    "startDate": "2025-10-01",
    "predictionDays": 5
  },
  "historicalData": [
    {
      "date": "2025-09-25",
      "open": 6000.0,
      "high": 6100.0,
      "low": 5950.0,
      "close": 6050.0,
      "volume": 500.0
    },
    // ... 更多歷史資料
  ],
  "predictions": [
    {
      "date": "2025-10-01",
      "predictedClose": 6100.5,
      "upProbability": 0.65,
      "changePercent": 0.83,
      "confidenceInterval": {
        "lower": 6050.0,
        "upper": 6150.0
      }
    },
    {
      "date": "2025-10-02",
      "predictedClose": 6120.3,
      "upProbability": 0.58,
      "changePercent": 0.32,
      "confidenceInterval": {
        "lower": 6070.0,
        "upper": 6170.0
      }
    }
    // ... 未來 5 天的預測
  ],
  "metadata": {
    "predictedAt": "2025-11-13T23:00:00",
    "executionTime": 2.5
  }
}
```

**欄位說明**：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `requestInfo.*` | Object | 請求資訊（便於前端顯示） |
| `historicalData` | Array | 歷史股價資料（用於圖表繪製） |
| `historicalData[].date` | String | 日期 |
| `historicalData[].close` | Float | 收盤價 |
| `predictions` | Array | 預測結果陣列 |
| `predictions[].date` | String | 預測日期 |
| `predictions[].predictedClose` | Float | 預測收盤價 |
| `predictions[].upProbability` | Float | 漲的機率（0-1） |
| `predictions[].changePercent` | Float | 相對於前一日的變化百分比 |
| `predictions[].confidenceInterval` | Object | 預測區間（可選，未來擴展） |
| `metadata.predictedAt` | String | 預測執行時間 |
| `metadata.executionTime` | Float | 執行耗時（秒） |

**範例 Python 類別**：
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class HistoricalDataPoint:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class PredictionDataPoint:
    date: str
    predicted_close: float
    up_probability: float
    change_percent: float

@dataclass
class PredictionResult:
    request_info: Dict
    historical_data: List[HistoricalDataPoint]
    predictions: List[PredictionDataPoint]
    metadata: Dict
    
    def to_dict(self) -> dict:
        return {
            "requestInfo": self.request_info,
            "historicalData": [
                {
                    "date": point.date,
                    "open": point.open,
                    "high": point.high,
                    "low": point.low,
                    "close": point.close,
                    "volume": point.volume
                }
                for point in self.historical_data
            ],
            "predictions": [
                {
                    "date": point.date,
                    "predictedClose": point.predicted_close,
                    "upProbability": point.up_probability,
                    "changePercent": point.change_percent
                }
                for point in self.predictions
            ],
            "metadata": self.metadata
        }
```


---

### 2.6 訓練任務 (TrainingTask)

**描述**: 代表一次模型訓練的執行記錄。

**儲存方式**: JSON 元資料

**JSON 結構**：
```json
{
  "taskId": "task_001",
  "modelName": "台股預測 v1",
  "dataFileId": "file_a3f2b1c4",
  "predictionDays": 5,
  "status": "completed",
  "progress": {
    "currentEpoch": 50,
    "totalEpochs": 50,
    "currentLoss": 0.05,
    "currentValLoss": 0.08
  },
  "startedAt": "2025-11-13T22:00:00",
  "completedAt": "2025-11-13T22:20:00",
  "duration": 1200.5,
  "resultModelId": "model_001",
  "error": null
}
```

**欄位說明**：

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| taskId | String | 必填、唯一 | 任務唯一識別符 |
| modelName | String | 必填 | 模型名稱 |
| dataFileId | String | 必填 | 訓練資料檔案 ID |
| predictionDays | Integer | 必填 | 預測天數 |
| status | String | 必填 | 狀態：pending, running, completed, failed |
| progress | Object | 選填 | 訓練進度資訊 |
| startedAt | String | 必填 | 開始時間 |
| completedAt | String | 選填 | 完成時間 |
| duration | Float | 選填 | 訓練耗時（秒） |
| resultModelId | String | 選填 | 產生的模型 ID |
| error | String | 選填 | 錯誤訊息 |

---

### 2.7 超參數配置 (HyperparameterConfiguration)

**描述**: 模型訓練時使用的超參數設定（嵌入於 PredictionModel 中）。

**JSON 結構**：
```json
{
  "lstmUnits1": 64,
  "lstmUnits2": 32,
  "dropout": 0.2,
  "learningRate": 0.001,
  "batchSize": 32,
  "epochs": 50,
  "lookbackWindow": 60
}
```

---

## 三、關聯關係

### 3.1 實體關聯圖

```
DataFile (1) ──────< (N) PredictionModel
    │
    └───────< (N) TrainingTask ────> (1) PredictionModel
```

---

## 四、資料操作模式

### 4.1 元資料管理服務（MetadataService）

**設計理念**: 集中管理所有元資料的 CRUD 操作，確保原子性與一致性。

**核心方法**：
- add_data_file() - 新增資料檔案
- get_data_file() - 取得資料檔案
- list_data_files() - 列出所有資料檔案
- delete_data_file() - 刪除資料檔案（軟刪除）
- add_model() - 新增模型
- get_model() - 取得模型
- list_models() - 列出所有模型
- add_training_task() - 新增訓練任務
- update_training_task() - 更新訓練任務

---

## 五、憲章合規性檢查

| 憲章原則 | 檢查結果 | 說明 |
|----------|---------|------|
| I. 正體中文優先 | ✅ 符合 | 所有欄位說明使用正體中文 |
| II. 規格驅動開發 | ✅ 符合 | 基於 spec.md 的 Key Entities 設計 |
| III. 高品質可測試的 MVP | ✅ 符合 | 資料模型支援核心功能 |
| IV. 嚴格禁止過度設計 | ✅ 符合 | 使用檔案系統，避免資料庫複雜性 |
| V. Pythonic 與 PEP 8 | ✅ 符合 | 使用 dataclass、型別提示 |
| VII. 簡潔務實 | ✅ 符合 | JSON 元資料 + 檔案系統方案 |

---

**核准狀態**: 待審查  
**下一步**: 進入 API 合約設計階段 (contracts/api.yaml)
