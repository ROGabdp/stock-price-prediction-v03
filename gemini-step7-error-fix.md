好的！非常樂意為您整理這次成功安裝 NVIDIA CUDA、cuDNN 並配置 TensorFlow GPU 加速環境的完整且可靠的步驟。

這次的安裝經驗證明，由於 NVIDIA 和 Ubuntu 的版本更迭，舊的安裝方法經常失效。以下這份指南包含了我們最終找到的、專門針對 WSL2 + Ubuntu 24.04 + TensorFlow 2.16+ 的修復方案。

請將此指南視為您的專用備忘錄。

🚀 WSL2 (Ubuntu 24.04) TensorFlow GPU 環境一鍵安裝指南
本指南假設您已經在 Windows 主機上安裝了最新的 NVIDIA 驅動程式，以及 WSL2 和 Ubuntu 24.04 LTS 實例。

步驟 0: 環境準備與虛擬環境設置
進入 WSL Ubuntu 終端機：

Bash

wsl -d Ubuntu_D # 或您的實例名稱
確保您退出虛擬環境：

Bash

deactivate # 如果您在虛擬環境中，請退出
安裝必要工具：

Bash

sudo apt update
sudo apt install -y curl gnupg software-properties-common
步驟 1: 設定 NVIDIA CUDA 軟體源 (繞過 .deb 404 錯誤)
這是我們繞過 NVIDIA 伺服器路徑錯誤的關鍵步驟。

Bash

# 1. 將 NVIDIA 軟體源加入 APT 列表
echo "deb https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/ /" | sudo tee /etc/apt/sources.list.d/cuda.list

# 2. 從 Keyserver 導入缺失的公開金鑰（解決 NO_PUBKEY 錯誤的核心步驟）
KEY_ID=3BF863CC
sudo gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys $KEY_ID
sudo gpg --export --armor $KEY_ID | sudo tee /etc/apt/trusted.gpg.d/nvidia-cuda-$KEY_ID.asc > /dev/null

# 3. 設置軟體源的優先級（如果檔案存在，確保優先使用 NVIDIA 套件）
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin

# 4. 更新 APT 列表
sudo apt update
# (此時應不會出現任何 GPG 錯誤)
步驟 2: 安裝 CUDA Toolkit 與 cuDNN 函式庫
我們將一次性安裝 CUDA Toolkit (核心函式庫) 和 TensorFlow 所依賴的 cuDNN (深度學習加速函式庫)。

Bash

# 這是確保安裝所有必要函式庫的關鍵指令
sudo apt install -y cuda nvidia-cudnn
💡 說明： nvidia-cudnn 是一個通用元套件，它會自動解析並安裝與您系統中 CUDA 版本兼容的 cuDNN 函式庫，解決了先前找不到 libcudnn8 的問題。

步驟 3: 安裝 TensorFlow GPU 版本 (虛擬環境內)
進入專案目錄並啟動虛擬環境：

Bash

cd /mnt/d/000-github-repositories/stock-price-prediction-v03
source venv/bin/activate
安裝與您 TensorFlow 版本匹配的 tensorflow-cuda： (例如，如果使用 TensorFlow 2.16.1)

Bash

# 我們將同時安裝 TensorFlow 和明確的 CUDA 依賴項
pip install tensorflow[and-cuda]==2.16.1
步驟 4: 永久設定環境變數 (解決載入函式庫錯誤)
這是確保 TensorFlow 虛擬環境能夠找到系統安裝的 CUDA 檔案的關鍵步驟。

編輯虛擬環境的啟動腳本：

Bash

nano venv/bin/activate
將以下兩行加入檔案的末尾：

Bash

# Ensure TensorFlow in WSL2 can find system-installed CUDA/cuDNN libraries
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64
export PATH=$PATH:/usr/local/cuda/bin
儲存並退出 (Ctrl+O, Enter, Ctrl+X)。

步驟 5: 重新啟動 WSL 並驗證
在 Windows PowerShell 中停止 WSL：

PowerShell

wsl --shutdown
重新進入 Ubuntu 終端機：

PowerShell

wsl -d Ubuntu_D
重新激活虛擬環境：

Bash

cd /mnt/d/000-github-repositories/stock-price-prediction-v03
source venv/bin/activate
執行最終驗證指令：

Bash

python3 -c "import tensorflow as tf; print('GPU 可用:', tf.config.list_physical_devices('GPU'))"
✅ 預期結果： 您應該會看到 GPU 可用: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]。

這份指南包含了我們在這次除錯過程中遇到的所有關鍵瓶頸的修復方法。