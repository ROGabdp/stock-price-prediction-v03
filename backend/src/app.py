"""
Flask 應用程式進入點
初始化 Flask、CORS 配置、註冊 API 路由
"""
# 在 import TensorFlow 之前配置 GPU
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 抑制 TensorFlow INFO 和 WARNING 訊息

from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, CORS_ORIGINS
from utils.gpu_config import configure_gpu, print_device_info

# 配置 GPU（應用程式啟動時執行一次）
gpu_config = configure_gpu()

# 建立 Flask 應用程式
app = Flask(__name__)

# 將 GPU 配置資訊儲存在 app.config 中
app.config['GPU_CONFIG'] = gpu_config

# 配置 CORS
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})


# 健康檢查端點
@app.route("/api/health", methods=["GET"])
def health_check():
    """健康檢查端點"""
    return jsonify({"status": "healthy", "message": "股價預測系統運作正常"}), 200


# GPU 狀態端點
@app.route("/api/gpu-status", methods=["GET"])
def gpu_status():
    """取得 GPU 狀態資訊"""
    from utils.gpu_config import get_gpu_info

    gpu_info = get_gpu_info()
    return jsonify({
        "success": True,
        "data": {
            "gpuAvailable": gpu_info.get("available", False),
            "gpuCount": gpu_info.get("count", 0),
            "devices": gpu_info.get("devices", []),
            "deviceType": app.config['GPU_CONFIG'].get('device_type', 'CPU'),
        }
    }), 200


# 根路徑
@app.route("/", methods=["GET"])
def root():
    """根路徑，顯示 API 資訊"""
    return jsonify(
        {
            "name": "股價漲跌機率預測系統 API",
            "version": "1.0.0",
            "endpoints": {
                "健康檢查": "/api/health",
                "資料管理": "/api/data/*",
                "模型訓練": "/api/models/train",
                "模型管理": "/api/models",
                "預測執行": "/api/predict",
            },
        }
    ), 200


# 錯誤處理
@app.errorhandler(404)
def not_found(error):
    """404 錯誤處理"""
    return jsonify({"success": False, "error": "找不到指定的資源"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 錯誤處理"""
    return jsonify({"success": False, "error": "伺服器內部錯誤"}), 500


# 註冊 API 路由
def register_routes():
    """註冊所有 API 路由"""
    from api.data_routes import data_bp
    from api.model_routes import model_bp
    from api.training_routes import training_bp
    from api.prediction_routes import prediction_bp
    from api.comparison_routes import comparison_bp

    # 註冊資料管理路由
    app.register_blueprint(data_bp, url_prefix="/api/data")

    # 註冊模型管理路由
    app.register_blueprint(model_bp, url_prefix="/api/models")

    # 註冊訓練任務路由
    app.register_blueprint(training_bp, url_prefix="/api/models")

    # 註冊預測路由
    app.register_blueprint(prediction_bp, url_prefix="/api")

    # 註冊模型比較路由
    app.register_blueprint(comparison_bp, url_prefix="/api/models")


# 註冊路由
register_routes()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("股價漲跌機率預測系統 - 後端伺服器")
    print("=" * 60)
    print(f"伺服器位址: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"API 端點: http://{FLASK_HOST}:{FLASK_PORT}/api")
    print(f"健康檢查: http://{FLASK_HOST}:{FLASK_PORT}/api/health")
    print("=" * 60)

    # 顯示裝置資訊
    print_device_info()

    print("按 Ctrl+C 停止伺服器")
    print("=" * 60 + "\n")

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
