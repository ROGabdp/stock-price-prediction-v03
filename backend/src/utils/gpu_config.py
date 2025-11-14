"""
GPU 配置工具模組
自動偵測並配置 TensorFlow GPU 使用
"""
import os


def configure_gpu():
    """
    配置 TensorFlow GPU 使用

    自動偵測系統是否有 NVIDIA GPU，如果有則配置使用 GPU，
    否則使用 CPU。同時配置記憶體成長模式避免 OOM 錯誤。

    回傳:
        dict: GPU 配置資訊
            - gpu_available (bool): GPU 是否可用
            - gpu_devices (list): 可用的 GPU 裝置列表
            - device_type (str): 使用的裝置類型 ('GPU' 或 'CPU')
    """
    try:
        import tensorflow as tf

        # 取得可用的 GPU 裝置
        gpus = tf.config.list_physical_devices('GPU')

        if gpus:
            try:
                # 配置 GPU 記憶體成長模式（避免一次占用所有記憶體）
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)

                # 設定可見的 GPU（預設使用所有 GPU）
                # tf.config.set_visible_devices(gpus[0], 'GPU')  # 若只想使用第一個 GPU

                print("=" * 60)
                print(f"✓ 偵測到 {len(gpus)} 個 NVIDIA GPU 裝置")
                for i, gpu in enumerate(gpus):
                    print(f"  GPU {i}: {gpu.name}")
                print("✓ GPU 記憶體成長模式已啟用")
                print("✓ 訓練將使用 GPU 加速")
                print("=" * 60)

                return {
                    "gpu_available": True,
                    "gpu_devices": [gpu.name for gpu in gpus],
                    "device_type": "GPU",
                    "gpu_count": len(gpus),
                }

            except RuntimeError as e:
                # GPU 配置失敗（例如記憶體不足）
                print("=" * 60)
                print(f"⚠ GPU 配置失敗: {e}")
                print("⚠ 將使用 CPU 進行訓練")
                print("=" * 60)

                return {
                    "gpu_available": False,
                    "gpu_devices": [],
                    "device_type": "CPU",
                    "error": str(e),
                }
        else:
            print("=" * 60)
            print("ℹ 未偵測到 NVIDIA GPU")
            print("ℹ 訓練將使用 CPU")
            print("=" * 60)

            return {
                "gpu_available": False,
                "gpu_devices": [],
                "device_type": "CPU",
            }

    except ImportError:
        print("=" * 60)
        print("⚠ TensorFlow 未安裝，無法配置 GPU")
        print("=" * 60)

        return {
            "gpu_available": False,
            "gpu_devices": [],
            "device_type": "CPU",
            "error": "TensorFlow not installed",
        }


def get_gpu_info():
    """
    取得 GPU 資訊（不進行配置）

    回傳:
        dict: GPU 資訊
    """
    try:
        import tensorflow as tf

        gpus = tf.config.list_physical_devices('GPU')

        if gpus:
            gpu_details = []
            for gpu in gpus:
                try:
                    # 嘗試取得 GPU 詳細資訊
                    gpu_details.append({
                        "name": gpu.name,
                        "type": gpu.device_type,
                    })
                except Exception:
                    gpu_details.append({
                        "name": gpu.name,
                        "type": "GPU",
                    })

            return {
                "available": True,
                "count": len(gpus),
                "devices": gpu_details,
            }
        else:
            return {
                "available": False,
                "count": 0,
                "devices": [],
            }

    except Exception as e:
        return {
            "available": False,
            "count": 0,
            "devices": [],
            "error": str(e),
        }


def print_device_info():
    """印出目前使用的裝置資訊"""
    try:
        import tensorflow as tf

        print("\n" + "=" * 60)
        print("TensorFlow 裝置資訊")
        print("=" * 60)
        print(f"TensorFlow 版本: {tf.__version__}")

        # CPU 資訊
        cpus = tf.config.list_physical_devices('CPU')
        print(f"CPU 裝置數量: {len(cpus)}")

        # GPU 資訊
        gpus = tf.config.list_physical_devices('GPU')
        print(f"GPU 裝置數量: {len(gpus)}")

        if gpus:
            for i, gpu in enumerate(gpus):
                print(f"  GPU {i}: {gpu.name}")

        # 邏輯裝置
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(f"邏輯 GPU 裝置數量: {len(logical_gpus)}")

        print("=" * 60 + "\n")

    except Exception as e:
        print(f"無法取得裝置資訊: {e}")
