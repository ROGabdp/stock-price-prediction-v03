# WSL2 GPU 加速完整設定指南

本指南將協助您在 WSL2 環境中啟用 NVIDIA GPU 加速，使用最新版 TensorFlow 2.15。

## 為什麼選擇 WSL2？

- ✅ 使用最新版 TensorFlow 2.15
- ✅ CUDA 自動管理，無需手動安裝
- ✅ 不會與 Windows 上的 CUDA 12.9 衝突
- ✅ GPU 效能接近原生（約 95%）
- ✅ 設定簡單，維護容易

## 前置需求

- Windows 10 版本 21H2 或更高 / Windows 11
- NVIDIA GPU 驅動 **已安裝**（您已有 576.80，符合要求）
- 系統管理員權限

## 安裝步驟

### 步驟 1: 安裝 WSL2

1. **以系統管理員身分開啟 PowerShell**
   - 按 `Win + X`，選擇「Windows PowerShell (系統管理員)」

2. **執行安裝指令**
   ```powershell
   wsl --install
   ```

3. **等待安裝完成**
   - 系統會自動下載並安裝 Ubuntu
   - 看到提示後，**重新啟動電腦**

4. **首次設定 Ubuntu**
   - 重啟後，Ubuntu 會自動開啟
   - 建立 Linux 使用者名稱和密碼
   ```
   Enter new UNIX username: [輸入您的使用者名稱]
   New password: [輸入密碼]
   Retype new password: [再次輸入密碼]
   ```

### 步驟 2: 驗證 WSL2 安裝

在 PowerShell 中執行：
```powershell
wsl --list --verbose
```

確認輸出類似：
```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

**VERSION 必須是 2**。如果是 1，執行：
```powershell
wsl --set-version Ubuntu 2
```

### 步驟 3: 驗證 GPU 可用性

在 WSL2 Ubuntu 終端機中執行：
```bash
nvidia-smi
```

應該會看到您的 RTX 4070 資訊。如果看到，表示 GPU 驅動正常！

### 步驟 4: 安裝 Python 環境

在 WSL2 Ubuntu 中執行：

```bash
# 更新套件列表
sudo apt update

# 安裝 Python 和必要工具
sudo apt install -y python3 python3-pip python3-venv

# 驗證安裝
python3 --version  # 應顯示 Python 3.x
```

### 步驟 5: 複製專案到 WSL2

**選項 A: 直接存取 Windows 檔案**（推薦，不需複製）
```bash
# Windows 的 D: 磁碟機在 WSL2 中的路徑是 /mnt/d
cd /mnt/d/000-github-repositories/stock-price-prediction-v03
```

**選項 B: 複製到 WSL2 檔案系統**（效能更好）
```bash
# 複製專案到 WSL2 家目錄
cp -r /mnt/d/000-github-repositories/stock-price-prediction-v03 ~/
cd ~/stock-price-prediction-v03
```

### 步驟 6: 建立虛擬環境並安裝依賴

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate

# 升級 pip
pip install --upgrade pip

# 安裝 TensorFlow GPU 版本（會自動安裝 CUDA）
pip install tensorflow[and-cuda]==2.15.0

# 安裝其他依賴
pip install -r backend/requirements.txt
```

### 步驟 7: 驗證 TensorFlow GPU

```bash
python3 -c "import tensorflow as tf; print('TensorFlow 版本:', tf.__version__); print('GPU 可用:', tf.config.list_physical_devices('GPU'))"
```

預期輸出：
```
TensorFlow 版本: 2.15.0
GPU 可用: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

### 步驟 8: 啟動後端伺服器

```bash
cd backend/src
python3 app.py
```

應該會看到：
```
============================================================
✓ 偵測到 1 個 NVIDIA GPU 裝置
  GPU 0: /physical_device:GPU:0
✓ GPU 記憶體成長模式已啟用
✓ 訓練將使用 GPU 加速
============================================================
```

### 步驟 9: 存取前端（從 Windows）

前端仍在 Windows 上執行，使用瀏覽器訪問：
```
http://localhost:5000
```

## 使用技巧

### 在 WSL2 中快速切換到專案

編輯 WSL2 的 `~/.bashrc`：
```bash
nano ~/.bashrc
```

在檔案末尾加入：
```bash
# 快速切換到專案
alias cdproject='cd /mnt/d/000-github-repositories/stock-price-prediction-v03 && source venv/bin/activate'
```

儲存後，執行：
```bash
source ~/.bashrc
```

之後只要輸入 `cdproject` 就能快速進入專案並啟動虛擬環境。

### WSL2 與 Windows 檔案互訪

- **從 WSL2 存取 Windows**: `/mnt/c/`, `/mnt/d/`
- **從 Windows 存取 WSL2**: `\\wsl$\Ubuntu\home\你的使用者名稱\`

### 停止 WSL2（節省資源）

不使用時可以停止 WSL2：
```powershell
# 在 PowerShell 中執行
wsl --shutdown
```

## 常見問題

### Q1: 安裝後看不到 GPU

**解決方法**:
1. 確認 NVIDIA 驅動版本夠新（您的 576.80 沒問題）
2. 重新啟動 WSL2：
   ```powershell
   wsl --shutdown
   wsl
   ```

### Q2: 安裝 TensorFlow 時出現錯誤

**解決方法**:
```bash
# 先安裝構建工具
sudo apt install -y build-essential

# 再次嘗試安裝
pip install tensorflow[and-cuda]==2.15.0
```

### Q3: WSL2 使用的記憶體太多

**解決方法**:
在 Windows 使用者目錄建立 `.wslconfig` 檔案（`C:\Users\你的使用者名稱\.wslconfig`）：
```ini
[wsl2]
memory=8GB
processors=4
```

### Q4: 想要回到 Windows 環境

無需移除 WSL2，兩者可以共存：
- WSL2 用於 GPU 訓練
- Windows 用於其他開發

## 效能比較

使用 RTX 4070 訓練 7976 筆資料：

| 環境 | 訓練時間 | 設定難度 |
|------|---------|---------|
| Windows CPU | ~20-30 分鐘 | ★☆☆☆☆ |
| Windows + CUDA 11.2 | ~3-5 分鐘 | ★★★★☆ |
| WSL2 + GPU | ~4-6 分鐘 | ★★★☆☆ |

**結論**: WSL2 提供接近原生的 GPU 效能，但設定簡單得多！

## 疑難排解

### 檢查 WSL2 版本
```powershell
wsl --version
```

### 更新 WSL2
```powershell
wsl --update
```

### 列出所有 WSL2 發行版
```powershell
wsl --list --all
```

### 重設 Ubuntu（清除所有資料）
```powershell
wsl --unregister Ubuntu
wsl --install
```

## 參考資料

- [WSL2 官方文件](https://learn.microsoft.com/zh-tw/windows/wsl/install)
- [TensorFlow on WSL2](https://www.tensorflow.org/install/pip#windows-wsl2)
- [NVIDIA CUDA on WSL2](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
- [WSL2 GPU 支援](https://learn.microsoft.com/zh-tw/windows/wsl/tutorials/gpu-compute)

---

**需要協助？** 如果遇到問題，請參考上方的「常見問題」章節。
