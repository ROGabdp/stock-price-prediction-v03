# 技術研究文件

**功能**: 股價漲跌機率預測系統  
**分支**: `001-stock-price-prediction`  
**日期**: 2025-11-13

## 執行摘要

本文件記錄股價預測系統的技術選型決策，遵循憲章「簡潔務實」與「嚴格禁止過度設計」原則，選擇最成熟、文件齊全且學習曲線平緩的技術方案。

**核心決策**：
- **後端框架**: Flask（輕量、易上手、文件豐富）
- **ML 框架**: TensorFlow + Keras（API 簡潔、適合 LSTM）
- **超參數調整**: Keras Tuner（與 Keras 無縫整合）
- **前端方案**: 原生 JavaScript + Chart.js（避免框架複雜性）
- **專案結構**: 前後端分離（清晰職責分離）

---

## 一、後端技術決策

### 1.1 Web 框架選擇

#### **決策**: Flask

**理由**：
- **簡潔性**: Flask 是微框架，核心簡單，適合 MVP 開發
- **學習曲線**: 文件豐富，上手快速，適合快速開發
- **靈活性**: 可依需求選擇擴展，避免過度設計
- **社群支援**: 成熟穩定，Stack Overflow 問題解答豐富
- **符合 MVP 原則**: 初期只需 RESTful API，無需複雜的管理後台

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **FastAPI** | 效能優異、自動 API 文件、型別檢查 | 需學習 Pydantic、async 概念、相對較新 | 對於 MVP，效能優勢不明顯；async 增加複雜度 |
| **Django** | 功能完整、內建管理後台、ORM 強大 | 重量級、學習曲線陡峭、過多內建功能 | 違反「避免過度設計」原則；不需要 ORM、用戶系統 |

**風險與權衡**：
- **風險**: Flask 需手動整合各套件（CORS、檔案上傳等）
- **緩解**: 使用成熟擴展（Flask-CORS、Werkzeug）
- **權衡**: 犧牲部分開箱即用功能，換取簡潔性與可控性

---

### 1.2 機器學習框架

#### **決策**: TensorFlow 2.x + Keras API

**理由**：
- **LSTM 支援**: Keras 提供高階 LSTM API，程式碼簡潔
- **易用性**: Keras Sequential API 適合快速建構神經網路
- **文件完整**: 官方文件與教學資源豐富
- **生態系統**: 與 Keras Tuner 無縫整合
- **穩定性**: TensorFlow 2.x 已成熟穩定

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **PyTorch** | 動態圖靈活、研究社群首選 | 學習曲線較陡、部署相對複雜 | MVP 不需動態圖靈活性；Keras API 更直觀 |
| **純 Keras** | API 最簡潔 | 已整合進 TensorFlow，獨立版不再維護 | 使用 TensorFlow 內建 Keras 即可 |

**範例程式碼**（簡潔性示範）：
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# 建構 LSTM 模型（僅需數行）
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(timesteps, features)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25, activation='relu'),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
```

**風險與權衡**：
- **風險**: TensorFlow 佔用較多記憶體
- **緩解**: 使用批次訓練、適當設定 batch_size
- **權衡**: 犧牲部分記憶體效率，換取開發速度與易用性

---

### 1.3 超參數調整工具

#### **決策**: Keras Tuner

**理由**：
- **整合性**: 專為 Keras 設計，API 一致性高
- **簡單性**: 配置簡單，支援多種搜索策略（Random、Hyperband、Bayesian）
- **無縫銜接**: 與 TensorFlow/Keras 模型定義無縫整合
- **文件齊全**: 官方文件清晰，範例豐富

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **Optuna** | 框架無關、視覺化好、彈性高 | 需額外學習 API、與 Keras 整合需適配層 | 增加學習成本；Keras Tuner 已足夠 |
| **Hyperopt** | 強大的貝葉斯優化 | API 較複雜、文件相對陳舊 | 學習曲線陡峭；對 MVP 功能過剩 |
| **手動網格搜尋** | 完全可控 | 耗時長、無智慧搜索 | 效率低；違反「使用成熟函式庫」原則 |

**範例程式碼**：
```python
import keras_tuner as kt

def build_model(hp):
    model = Sequential([
        LSTM(units=hp.Int('lstm_units', min_value=32, max_value=128, step=32),
             return_sequences=True, input_shape=(timesteps, features)),
        Dropout(hp.Float('dropout', min_value=0.1, max_value=0.5, step=0.1)),
        LSTM(units=hp.Int('lstm_units_2', min_value=32, max_value=128, step=32)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

tuner = kt.Hyperband(build_model, objective='val_loss', max_epochs=50)
```

**風險與權衡**：
- **風險**: 超參數搜索耗時長
- **緩解**: 使用 Hyperband 策略（早停機制）、限制搜索空間
- **權衡**: 訓練時間略長，換取模型準確率提升


---

### 1.4 資料處理套件

#### **決策**: pandas

**理由**：
- **標準工具**: Python 資料處理的事實標準
- **CSV 原生支援**: `pd.read_csv()` 功能強大且穩定
- **日期處理**: 內建日期解析與時間序列操作
- **資料驗證**: 易於檢查缺失值、異常值

**無爭議決策**：pandas 是業界共識，無需評估替代方案。

**範例程式碼**：
```python
import pandas as pd

# 載入 CSV 並解析日期
df = pd.read_csv('data.csv', parse_dates=['date'])
df = df.sort_values('date')  # 確保時間序列排序

# 驗證必要欄位
required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
if not all(col in df.columns for col in required_cols):
    raise ValueError("缺少必要欄位")
```

---

### 1.5 模型持久化

#### **決策**: TensorFlow SavedModel 格式（`.keras` 檔案）

**理由**：
- **官方推薦**: TensorFlow 2.x 推薦格式
- **完整性**: 儲存模型架構、權重、優化器狀態
- **跨平台**: 可在不同環境載入
- **簡單性**: `model.save()` 與 `load_model()` 即可

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **HDF5 (`.h5`)** | 輕量、向後相容 | 未來可能淘汰 | TensorFlow 官方已推薦 SavedModel |
| **pickle** | Python 通用 | 不安全、版本相依性高 | 不適合儲存深度學習模型 |

**範例程式碼**：
```python
# 儲存模型
model.save('models/stock_model_v1.keras')

# 載入模型
from tensorflow.keras.models import load_model
model = load_model('models/stock_model_v1.keras')
```

---

### 1.6 日期處理

#### **決策**: pandas + Python `datetime`

**理由**：
- **內建功能**: pandas 內建日期解析與格式化
- **無需額外依賴**: 避免引入 `dateutil`、`arrow` 等套件
- **符合簡潔原則**: 標準庫足以應對需求

**範例程式碼**：
```python
# 解析多種日期格式
df['date'] = pd.to_datetime(df['date'], format='mixed')  # 支援 YYYY/M/D 與 YYYY-MM-DD

# 驗證日期範圍
if prediction_date < df['date'].min() or prediction_date > df['date'].max():
    raise ValueError("預測起始日期超出資料範圍")
```

---

## 二、前端技術決策

### 2.1 前端框架選擇

#### **決策**: 原生 JavaScript（ES6+）

**理由**：
- **避免過度設計**: Vue/React 對於簡單 UI 是過度工程
- **學習曲線**: 無需學習框架生態系統（路由、狀態管理等）
- **快速開發**: 無需打包工具、無需複雜配置
- **符合 MVP**: 專案 UI 互動簡單，不需要複雜狀態管理
- **部署簡單**: 直接開啟 HTML 即可，無需 build 流程

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **Vue.js** | 易學、雙向綁定、元件化 | 需學習框架、需打包工具 | 對於簡單表單與圖表顯示，過度設計 |
| **React** | 生態豐富、元件化 | 學習曲線陡、需 JSX、需打包 | 複雜度不符合 MVP 需求 |

**HTML 結構範例**（簡潔性示範）：
```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>股價預測系統</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>模型訓練</h1>
    <form id="trainForm">
        <label>選擇資料檔案：
            <select id="dataFile"></select>
        </label>
        <label>模型名稱：
            <input type="text" id="modelName" required>
        </label>
        <label>預測天數 (1-30)：
            <input type="number" id="predictionDays" min="1" max="30" value="5">
        </label>
        <button type="submit">開始訓練</button>
    </form>
    <div id="progress" style="display:none;">
        <p>訓練進度：<span id="epoch"></span></p>
    </div>
    <script src="js/train.js"></script>
</body>
</html>
```

**風險與權衡**：
- **風險**: UI 程式碼可能較冗長（相比框架）
- **緩解**: 使用模組化 JS 檔案分離關注點
- **權衡**: 犧牲部分開發便利性，換取簡潔性與零配置

---

### 2.2 圖表視覺化函式庫

#### **決策**: Chart.js

**理由**：
- **簡單易用**: API 直觀，配置簡單
- **CDN 可用**: 無需打包，直接引入即可
- **互動功能**: 內建縮放、懸停顯示數值等功能
- **文件齊全**: 官方文件與範例豐富
- **輕量級**: 體積小，載入快速
- **符合需求**: 支援折線圖、多資料集（歷史 vs 預測）

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **Plotly.js** | 功能豐富、3D 圖表 | 體積大、配置複雜 | 功能過剩；不需要 3D 圖表 |
| **D3.js** | 高度客製化、強大 | 學習曲線陡峭、程式碼複雜 | 違反簡潔原則；Chart.js 足夠 |
| **ECharts** | 功能豐富、中文文件 | 體積較大、API 複雜 | 對於簡單折線圖，過度設計 |

**範例程式碼**：
```javascript
const ctx = document.getElementById('chart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,  // ['2025-10-01', '2025-10-02', ...]
        datasets: [
            {
                label: '歷史股價',
                data: historicalPrices,
                borderColor: 'blue',
                borderWidth: 2,
                fill: false
            },
            {
                label: '預測股價',
                data: predictedPrices,
                borderColor: 'red',
                borderWidth: 2,
                borderDash: [5, 5],  // 虛線表示預測
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            tooltip: { mode: 'index' }
        },
        scales: {
            x: { display: true, title: { display: true, text: '日期' } },
            y: { display: true, title: { display: true, text: '股價' } }
        }
    }
});
```

**風險與權衡**：
- **風險**: 大量資料點可能影響效能
- **緩解**: 限制顯示範圍、使用資料抽樣（若資料超過 1000 點）
- **權衡**: 可接受的效能，換取簡潔的實作


---

### 2.3 日期選擇器

#### **決策**: HTML5 原生 `<input type="date">`

**理由**：
- **零依賴**: 瀏覽器原生支援
- **自動驗證**: 瀏覽器自動驗證日期格式
- **符合簡潔原則**: 無需引入第三方函式庫
- **現代瀏覽器支援**: Chrome、Firefox、Edge 皆支援

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **Flatpickr** | 功能豐富、可客製化 | 需額外依賴 | 原生 input 已足夠 |
| **Date Range Picker** | 支援範圍選擇 | 不需要範圍選擇功能 | 功能過剩 |

**範例程式碼**：
```html
<label>預測起始日期：
    <input type="date" id="startDate" required>
</label>
```

---

### 2.4 檔案上傳處理

#### **決策**: HTML5 原生 `<input type="file">` + Fetch API

**理由**：
- **原生支援**: 無需第三方函式庫
- **FormData API**: 支援檔案上傳
- **符合簡潔原則**: 標準 Web API 足夠

**範例程式碼**：
```javascript
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', document.getElementById('csvFile').files[0]);
    
    const response = await fetch('/api/data/upload', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        const result = await response.json();
        alert(`上傳成功：${result.message}`);
    } else {
        const error = await response.json();
        alert(`上傳失敗：${error.error}`);
    }
});
```

---

### 2.5 HTTP 客戶端

#### **決策**: Fetch API

**理由**：
- **原生支援**: 所有現代瀏覽器內建
- **Promise 基礎**: 支援 async/await
- **無需依賴**: 避免引入 axios

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **axios** | 自動 JSON 轉換、攔截器 | 需額外依賴 | Fetch API 已足夠 |

**範例程式碼**：
```javascript
async function fetchModels() {
    try {
        const response = await fetch('/api/models');
        if (!response.ok) throw new Error('載入失敗');
        const models = await response.json();
        return models;
    } catch (error) {
        console.error('錯誤:', error);
        alert('載入模型清單失敗');
    }
}
```

---

## 三、架構設計決策

### 3.1 前後端通訊協定

#### **決策**: RESTful API (JSON)

**理由**：
- **簡單直觀**: 符合 HTTP 語義（GET、POST、DELETE）
- **無狀態**: 易於測試與擴展
- **標準化**: 業界標準，易於理解
- **符合需求**: 專案不需要即時通訊（WebSocket）

**API 設計範例**：
- `GET /api/models` - 取得模型清單
- `POST /api/models/train` - 訓練新模型
- `POST /api/predict` - 執行預測
- `DELETE /api/models/{modelId}` - 刪除模型

---

### 3.2 專案結構

#### **決策**: 前後端分離

**理由**：
- **職責分離**: 前端專注 UI，後端專注 API 與 ML
- **獨立開發**: 可平行開發前後端
- **清晰邊界**: API 作為唯一介面
- **部署彈性**: 可獨立部署或合併部署

**目錄結構**：
```
stock-price-prediction-v03/
├── backend/
│   ├── src/
│   │   ├── api/         # Flask 路由
│   │   ├── models/      # 資料模型
│   │   ├── services/    # 業務邏輯
│   │   └── ml/          # ML 訓練與預測
│   ├── data/            # CSV 儲存
│   ├── models/          # 訓練模型儲存
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── train.js
│       ├── predict.js
│       └── api.js       # API 呼叫封裝
└── README.md
```

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **單一專案（Flask 渲染 HTML）** | 簡單、無 CORS 問題 | 前後端耦合、不易擴展 | 違反職責分離原則 |

---

### 3.3 開發伺服器設定

#### **決策**: Flask 後端 + Python HTTP Server 前端

**理由**：
- **簡單性**: 無需 Nginx 等複雜配置
- **開發友善**: 快速啟動測試
- **CORS 處理**: 使用 Flask-CORS 解決跨域問題

**啟動方式**：
```bash
# 後端（預設 port 5000）
cd backend
python -m flask run

# 前端（port 8000）
cd frontend
python -m http.server 8000
```

---

### 3.4 靜態檔案服務

#### **決策**: Flask 僅提供 API，前端靜態檔案由獨立 HTTP Server 服務

**理由**：
- **職責分離**: Flask 專注 API 邏輯
- **開發便利**: 前端修改無需重啟後端
- **符合架構**: 前後端分離原則

**替代方案（生產環境）**：
- 可使用 Flask 的 `send_from_directory` 合併部署
- 可使用 Nginx 反向代理

---

## 四、開發工具決策

### 4.1 Python 虛擬環境管理

#### **決策**: venv（Python 內建）

**理由**：
- **內建工具**: Python 3.3+ 內建，無需額外安裝
- **輕量**: 功能足夠，符合簡潔原則
- **標準化**: 官方推薦

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **conda** | 管理二進位依賴、多 Python 版本 | 重量級、安裝慢 | 專案不需要複雜環境管理 |
| **poetry** | 現代化、依賴解析好 | 學習曲線、配置複雜 | venv + pip 已足夠 |

---

### 4.2 套件管理

#### **決策**: pip + requirements.txt

**理由**：
- **標準工具**: Python 官方套件管理器
- **簡單**: 單一檔案記錄依賴
- **廣泛支援**: 所有 CI/CD 工具支援

**requirements.txt 範例**：
```
flask==3.0.0
flask-cors==4.0.0
tensorflow==2.15.0
keras-tuner==1.4.6
pandas==2.1.4
numpy==1.26.2
```

---

### 4.3 程式碼格式化

#### **決策**: black + flake8

**理由**：
- **black**: 自動格式化，零配置，符合 PEP 8
- **flake8**: 靜態檢查，偵測潛在錯誤
- **業界標準**: 被廣泛採用

**配置範例** (`.flake8`)：
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

---

### 4.4 前端打包工具

#### **決策**: 不使用（開發階段）

**理由**：
- **避免複雜性**: Webpack、Vite 對於原生 JS 不必要
- **直接引入 CDN**: Chart.js 等函式庫直接使用 CDN
- **符合 MVP**: 開發階段無需打包

**未來考慮**（生產環境優化）：
- 可使用簡單的 minify 工具壓縮 JS/CSS


---

## 五、儲存方案決策

### 5.1 資料儲存策略

#### **決策**: 檔案系統（無資料庫）

**理由**：
- **簡單性**: 避免資料庫安裝與配置
- **符合規模**: 預估 50 個模型、100 個檔案，檔案系統足夠
- **易於備份**: 直接複製資料夾即可
- **符合憲章**: 嚴格禁止過度設計

**儲存結構**：
```
backend/
├── data/
│   ├── uploaded/
│   │   ├── file_001_台股歷史資料.csv
│   │   └── file_002_美股資料.csv
│   └── metadata.json  # 記錄檔案元資料（名稱、匯入時間、範圍）
├── models/
│   ├── model_001_台股預測v1.keras
│   ├── model_001_metadata.json  # 模型元資料
│   └── model_002_台股預測v2.keras
└── logs/
    └── training.log
```

**metadata.json 範例**：
```json
{
  "dataFiles": [
    {
      "fileId": "file_001",
      "fileName": "台股歷史資料.csv",
      "uploadedAt": "2025-11-13T22:00:00",
      "dateRange": {
        "start": "1994-05-13",
        "end": "2025-11-11"
      },
      "rowCount": 7890
    }
  ],
  "models": [
    {
      "modelId": "model_001",
      "modelName": "台股預測 v1",
      "trainedAt": "2025-11-13T22:30:00",
      "dataFileId": "file_001",
      "predictionDays": 5,
      "metrics": {
        "trainAccuracy": 0.78,
        "valAccuracy": 0.72,
        "loss": 0.05
      },
      "hyperparameters": {
        "lstmUnits": 64,
        "dropout": 0.2,
        "epochs": 50
      }
    }
  ]
}
```

**替代方案評估**：

| 方案 | 優點 | 缺點 | 排除理由 |
|------|------|------|----------|
| **SQLite** | 結構化查詢、ACID | 需 ORM 或 SQL、增加複雜度 | 資料量小，檔案系統足夠 |
| **PostgreSQL** | 強大、可擴展 | 安裝配置複雜、過度設計 | 違反簡潔原則；不符合單機環境 |

**風險與緩解**：
- **風險**: 檔案系統無事務保證，可能出現資料不一致
- **緩解**: 使用 JSON 原子寫入（先寫臨時檔案再重新命名）
- **權衡**: 可接受的風險，換取極大的簡潔性

---

### 5.2 模型儲存格式

#### **決策**: `.keras` 檔案（已於 1.5 節決定）

**命名規範**: `model_{modelId}_{modelName}.keras`

---

### 5.3 CSV 儲存管理

#### **決策**: 保留原檔案名稱 + UUID 前綴

**理由**：
- **可讀性**: 保留原檔案名稱方便識別
- **唯一性**: UUID 避免檔名衝突

**命名範例**：
```
file_a3f2b1c4_台股歷史資料.csv
file_d8e7f6a5_美股資料.csv
```

---

## 六、技術堆疊總結

### 後端 (Backend)

| 類別 | 技術 | 版本 |
|------|------|------|
| 語言 | Python | 3.11+ |
| Web 框架 | Flask | 3.0.0 |
| CORS | Flask-CORS | 4.0.0 |
| ML 框架 | TensorFlow + Keras | 2.15.0 |
| 超參數調整 | Keras Tuner | 1.4.6 |
| 資料處理 | pandas | 2.1.4 |
| 數值運算 | NumPy | 1.26.2 |
| 模型儲存 | TensorFlow SavedModel | - |
| 格式化 | black | 24.0.0 |
| Linter | flake8 | 7.0.0 |

### 前端 (Frontend)

| 類別 | 技術 | 版本 |
|------|------|------|
| 語言 | JavaScript | ES6+ |
| 框架 | 無（原生 JS） | - |
| 圖表 | Chart.js | 4.4.0 (CDN) |
| HTTP 客戶端 | Fetch API | 原生 |
| 日期選擇器 | HTML5 原生 | - |

### 開發工具

| 類別 | 技術 |
|------|------|
| 虛擬環境 | venv |
| 套件管理 | pip + requirements.txt |
| 版本控制 | Git |
| 程式碼格式化 | black + Prettier (JS) |
| Linter | flake8 + ESLint |

### 儲存與部署

| 類別 | 技術 |
|------|------|
| 資料儲存 | 檔案系統 + JSON |
| 開發伺服器 | Flask dev server + Python HTTP server |

---

## 七、風險評估與緩解策略

### 高風險項目

| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|----------|
| 模型訓練時間過長 | 使用者體驗差 | 高 | 使用 Hyperband 早停、限制搜索空間、顯示進度條 |
| 大檔案上傳失敗 | 功能無法使用 | 中 | 限制檔案大小（100MB）、分段上傳（未來優化） |
| 記憶體不足（訓練大模型） | 訓練失敗 | 中 | 使用批次訓練、適當設定 batch_size、監控記憶體 |

### 中風險項目

| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|----------|
| CSV 格式不符 | 資料無法載入 | 中 | 詳細錯誤訊息、提供範例檔案、驗證必要欄位 |
| 前端圖表效能不佳（大量資料點） | 顯示緩慢 | 低 | 資料抽樣、限制顯示範圍 |
| 檔案系統資料不一致 | 資料遺失 | 低 | JSON 原子寫入、定期備份 |

---

## 八、未來擴展考量（不在 MVP 範圍）

### 可能的技術升級路徑

1. **效能優化**：
   - 引入 Redis 快取預測結果
   - 使用 Celery 處理非同步訓練任務
   - 模型部署至 TensorFlow Serving

2. **資料庫遷移**：
   - 當模型數量 > 100 時，考慮遷移至 SQLite
   - 當需要多使用者時，遷移至 PostgreSQL

3. **前端升級**：
   - 當 UI 互動複雜度提升時，考慮引入 Vue.js
   - 使用 Vite 打包以優化載入速度

4. **安全性**：
   - 引入使用者認證（Flask-Login 或 JWT）
   - HTTPS 部署

**重要原則**: 這些升級必須在實際需求出現後才進行，避免預測性設計。

---

## 九、憲章合規性檢查

| 憲章原則 | 檢查結果 | 說明 |
|----------|---------|------|
| I. 正體中文優先 | ✅ 符合 | 所有文件、註解、UI 文字使用正體中文 |
| II. 規格驅動開發 | ✅ 符合 | 基於 spec.md 進行技術決策 |
| III. 高品質可測試的 MVP | ✅ 符合 | 專注 P1 故事（訓練與預測） |
| IV. 嚴格禁止過度設計 | ✅ 符合 | 選擇最簡單方案（原生 JS、檔案系統、Flask） |
| V. Pythonic 與 PEP 8 | ✅ 符合 | 使用 black + flake8 |
| VI. Idiomatic JavaScript | ✅ 符合 | 使用現代 ES6+ 語法 |
| VII. 簡潔務實 | ✅ 符合 | 優先使用成熟函式庫（pandas、Chart.js） |

**結論**: 所有技術決策符合憲章要求，無違規項目。

---

## 十、總結

本技術研究文件遵循「簡潔務實」與「嚴格禁止過度設計」原則，選擇最成熟、易用、文件齊全的技術方案：

- **後端**: Flask + TensorFlow/Keras + Keras Tuner
- **前端**: 原生 JavaScript + Chart.js
- **儲存**: 檔案系統 + JSON
- **架構**: 前後端分離 RESTful API

這套技術堆疊能確保：
1. **快速開發**: 學習曲線平緩，文件豐富
2. **高品質 MVP**: 專注核心功能（訓練與預測）
3. **易於維護**: 簡潔的架構，無過度抽象
4. **符合憲章**: 所有決策符合專案憲章要求

---

**核准狀態**: 待審查  
**下一步**: 進入資料模型設計階段 (data-model.md)
