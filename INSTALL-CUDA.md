# CUDA 安裝指南（TensorFlow 2.10 GPU 支援）

您的系統已安裝 CUDA 12.9，但 TensorFlow 2.10 需要 CUDA 11.2。

## 系統資訊

- **GPU**: NVIDIA GeForce RTX 4070
- **驅動版本**: 576.80
- **目前 CUDA**: 12.9
- **所需 CUDA**: 11.2

## 安裝步驟

### 方法 1: 安裝 CUDA 11.2（與現有 CUDA 12.9 共存）

1. **下載 CUDA Toolkit 11.2**

   前往 [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-11.2.0-download-archive)

   選擇：
   - Operating System: Windows
   - Architecture: x86_64
   - Version: 10/11
   - Installer Type: exe (local)

2. **安裝 CUDA 11.2**

   執行下載的安裝程式，選擇 "Custom" 安裝，取消勾選：
   - Visual Studio Integration（如果不需要）
   - Driver components（因為已有更新的驅動）

   只安裝：
   - CUDA Toolkit
   - CUDA Runtime
   - CUDA Libraries

3. **下載 cuDNN 8.1**

   前往 [NVIDIA cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive)

   下載: **cuDNN v8.1.1 for CUDA 11.0,11.1 and 11.2**

4. **安裝 cuDNN**

   解壓縮 cuDNN ZIP 檔案，將以下檔案複製到 CUDA 11.2 安裝目錄：

   ```
   從 cuDNN/bin/*.dll    → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin\
   從 cuDNN/include/*.h  → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\include\
   從 cuDNN/lib/*.lib    → C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\lib\x64\
   ```

5. **設定環境變數**

   將以下路徑加入系統 PATH（移至最前面）：
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\libnvvp
   ```

6. **重新啟動電腦**

   讓環境變數生效

7. **驗證安裝**

   ```bash
   # 檢查 CUDA 版本
   nvcc --version

   # 應該顯示: Cuda compilation tools, release 11.2
   ```

8. **測試 TensorFlow GPU**

   ```bash
   cd D:\000-github-repositories\stock-price-prediction-v03
   venv\Scripts\activate
   python -c "import tensorflow as tf; print('GPU:', tf.config.list_physical_devices('GPU'))"
   ```

### 方法 2: 使用 WSL2 + TensorFlow 2.15 GPU（推薦替代方案）

**優點**:
- 使用最新版 TensorFlow 2.15
- 完整的 GPU 支援，無需複雜的 CUDA 版本管理
- 一次設定，長期使用

**缺點**:
- 需要安裝 WSL2（約需 10-15 分鐘）
- 需要在 WSL2 環境中運行專案

**安裝步驟**:

1. **安裝 WSL2 和 Ubuntu**:
   ```bash
   # 在 PowerShell（以系統管理員身分執行）
   wsl --install
   ```

2. **在 WSL2 中安裝 TensorFlow GPU**:
   ```bash
   # 進入 WSL2 Ubuntu
   wsl

   # 安裝 Python 和 pip
   sudo apt update
   sudo apt install python3-pip python3-venv

   # 安裝 TensorFlow GPU（會自動安裝 CUDA）
   pip install tensorflow[and-cuda]==2.15.0
   ```

3. **在 WSL2 中執行專案**:
   ```bash
   # 複製專案到 WSL2 或直接存取 Windows 檔案
   cd /mnt/d/000-github-repositories/stock-price-prediction-v03
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

**注意**: WSL2 方式下，CUDA 會由 TensorFlow 自動管理，無需手動安裝。

### 方法 3: 保持使用 CPU（最簡單）

如果您不想處理 CUDA 安裝的複雜性：

```bash
# 解除安裝 GPU 版本
pip uninstall tensorflow-gpu

# 重新安裝 CPU 版本
pip install tensorflow==2.15.0
```

程式已經實作了自動偵測，會自動退回 CPU 訓練。

## 我的建議

根據您的情況，我建議：

### 短期方案（立即可用）
**保持使用 CPU（方法 3）**，因為：
1. ✓ 無需任何設定，現在就能用
2. ✓ 程式已優化（GPU 偵測、警告抑制）
3. ✓ 對於偶爾訓練模型，20-30 分鐘可接受
4. ✓ 先驗證系統功能正常

### 長期方案（如果經常訓練）
**安裝 CUDA 11.2（方法 1）**，因為：
1. ✓ 訓練速度最快（比 CPU 快 6-8 倍）
2. ✓ 完整的功能支援
3. ✓ 適合頻繁訓練大量模型
4. ✗ 初次設定較複雜（需時約 30-60 分鐘）

### 替代方案（如果熟悉 Linux）
**使用 WSL2（方法 2）**，因為：
1. ✓ 設定相對簡單
2. ✓ 使用最新版 TensorFlow
3. ✓ GPU 效能接近原生
4. ✗ 需要在 Linux 環境中操作

## 疑難排解

### 問題: DLL not found

確保 CUDA 11.2 的 bin 目錄在系統 PATH 的**最前面**。

### 問題: CUDA version mismatch

TensorFlow 2.10 需要特定版本：
- CUDA: 11.2
- cuDNN: 8.1

### 問題: Out of Memory

降低 batch_size 或 lookback_window。

## 效能比較

使用 RTX 4070 (8GB VRAM) 訓練 7976 筆資料的預估時間：

| 方法 | 預估訓練時間 | 相對速度 | 設定難度 |
|------|-------------|---------|---------|
| CPU（目前）| ~20-30 分鐘 | 1x（基準）| ★☆☆☆☆ 最簡單 |
| WSL2 + GPU | ~4-6 分鐘 | 5-6x | ★★★☆☆ 中等 |
| CUDA 11.2 + GPU（原生）| ~3-5 分鐘 | 6-8x | ★★★★☆ 複雜 |

**注意**:
- 實際訓練時間取決於超參數搜索的配置
- 首次訓練包含 Keras Tuner 的超參數調整階段，會額外增加時間
- 上述時間為單次完整訓練（包含資料預處理、超參數搜索、模型訓練）

## 參考資料

- [TensorFlow GPU 支援官方文件](https://www.tensorflow.org/install/gpu)
- [TensorFlow 版本相容性對照表](https://www.tensorflow.org/install/source#gpu)
- [CUDA Toolkit 11.2 下載](https://developer.nvidia.com/cuda-11.2.0-download-archive)
- [cuDNN Archive 下載](https://developer.nvidia.com/rdp/cudnn-archive)
- [WSL2 安裝指南](https://learn.microsoft.com/zh-tw/windows/wsl/install)
- [TensorFlow on WSL2 設定](https://www.tensorflow.org/install/pip#windows-wsl2)
