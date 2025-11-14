# GPU 加速設定指南

本系統已支援自動偵測並使用 NVIDIA GPU 進行訓練加速。

## 系統需求

### 硬體需求
- **NVIDIA GPU**: 支援 CUDA Compute Capability 3.5 或更高
- **顯示記憶體**: 建議至少 4GB VRAM

### 軟體需求
- **NVIDIA 驅動程式**: 最新版本
- **CUDA**: 自動安裝（透過 tensorflow[and-cuda]）
- **cuDNN**: 自動安裝（透過 tensorflow[and-cuda]）

## 安裝步驟

### 1. 檢查目前狀態

啟動後端伺服器，查看終端機輸出：

```bash
cd backend/src
python app.py
```

如果看到：
```
ℹ 未偵測到 NVIDIA GPU
ℹ 訓練將使用 CPU
```

表示目前使用 CPU，需要安裝 GPU 版本。

### 2. 安裝 GPU 版本的 TensorFlow

**重要**: 請先停止後端伺服器（Ctrl+C）

```bash
# 啟動虛擬環境（如果尚未啟動）
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 解除安裝 CPU 版本
pip uninstall tensorflow

# 安裝 GPU 版本（會自動安裝 CUDA 和 cuDNN）
pip install tensorflow[and-cuda]==2.15.0
```

### 3. 驗證 GPU 可用性

```bash
python -c "import tensorflow as tf; print('GPU 可用:', tf.config.list_physical_devices('GPU'))"
```

預期輸出（如果有 GPU）：
```
GPU 可用: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

### 4. 重新啟動後端

```bash
cd backend/src
python app.py
```

如果成功偵測到 GPU，應該會看到：
```
============================================================
✓ 偵測到 1 個 NVIDIA GPU 裝置
  GPU 0: /physical_device:GPU:0
✓ GPU 記憶體成長模式已啟用
✓ 訓練將使用 GPU 加速
============================================================
```

## 功能說明

### 自動偵測機制

系統在啟動時會自動執行以下操作：

1. **偵測 GPU**: 檢查系統是否有可用的 NVIDIA GPU
2. **配置記憶體成長**: 啟用 GPU 記憶體動態分配，避免 OOM 錯誤
3. **選擇裝置**:
   - 有 GPU → 使用 GPU 訓練
   - 無 GPU → 自動退回 CPU 訓練
4. **顯示資訊**: 在終端機顯示偵測結果

### API 端點

查詢 GPU 狀態：

```bash
GET http://localhost:5000/api/gpu-status
```

回應範例：
```json
{
  "success": true,
  "data": {
    "gpuAvailable": true,
    "gpuCount": 1,
    "devices": [
      {
        "name": "/physical_device:GPU:0",
        "type": "GPU"
      }
    ],
    "deviceType": "GPU"
  }
}
```

## 效能比較

使用 GPU 訓練的速度提升：

| 資料量 | CPU 時間 | GPU 時間 | 加速比 |
|--------|---------|---------|--------|
| 5K 筆  | ~10 分鐘 | ~2 分鐘  | 5x     |
| 10K 筆 | ~30 分鐘 | ~5 分鐘  | 6x     |
| 20K 筆 | ~60 分鐘 | ~10 分鐘 | 6x     |

*實際效能取決於 GPU 型號與 CPU 規格*

## 常見問題

### Q1: 安裝後仍顯示「未偵測到 NVIDIA GPU」

**可能原因**:
1. 顯卡驅動未安裝或版本過舊
2. 不是 NVIDIA GPU（AMD/Intel 顯卡不支援 CUDA）
3. TensorFlow 版本與 CUDA 不相容

**解決方法**:
```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 更新 NVIDIA 驅動至最新版本
# 從 https://www.nvidia.com/Download/index.aspx 下載
```

### Q2: 出現 CUDA OOM (Out of Memory) 錯誤

**解決方法**:
- 系統已啟用記憶體成長模式，通常不會發生
- 如果仍發生，可減少 batch_size 或 lookback_window

### Q3: 想要只使用特定 GPU（多 GPU 系統）

修改 `backend/src/utils/gpu_config.py`:

```python
# 只使用第一個 GPU
tf.config.set_visible_devices(gpus[0], 'GPU')
```

### Q4: 想要同時使用多個 GPU

TensorFlow 預設會使用所有可用的 GPU，無需額外配置。

## 回退到 CPU

如果想要回到 CPU 版本：

```bash
pip uninstall tensorflow
pip install tensorflow==2.15.0
```

系統會自動偵測並使用 CPU。

## 參考資料

- [TensorFlow GPU 支援官方文件](https://www.tensorflow.org/install/gpu)
- [CUDA 相容性列表](https://developer.nvidia.com/cuda-gpus)
- [TensorFlow 版本對應表](https://www.tensorflow.org/install/source#gpu)
