"""
模型訓練 API 路由
處理訓練任務的建立與監控
"""
from flask import Blueprint, request, jsonify
from services.training_service import get_training_service
from config import MIN_PREDICTION_DAYS, MAX_PREDICTION_DAYS

training_bp = Blueprint("training", __name__)
training_service = get_training_service()


@training_bp.route("/train", methods=["POST"])
def start_training():
    """啟動模型訓練"""
    try:
        data = request.get_json()

        # 驗證必要欄位
        if not data:
            return jsonify({"success": False, "error": "請求 body 不可為空"}), 400

        model_name = data.get("modelName")
        data_file_id = data.get("dataFileId")
        prediction_days = data.get("predictionDays")

        # 欄位驗證
        if not model_name:
            return jsonify({"success": False, "error": "請輸入模型名稱"}), 400

        if not data_file_id:
            return jsonify({"success": False, "error": "請選擇資料檔案"}), 400

        if not prediction_days:
            return jsonify({"success": False, "error": "請設定預測天數"}), 400

        # 預測天數範圍驗證
        try:
            prediction_days = int(prediction_days)
        except ValueError:
            return jsonify({"success": False, "error": "預測天數必須為整數"}), 400

        if not (MIN_PREDICTION_DAYS <= prediction_days <= MAX_PREDICTION_DAYS):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"預測天數必須在 {MIN_PREDICTION_DAYS} 到 {MAX_PREDICTION_DAYS} 天之間",
                    }
                ),
                400,
            )

        # 啟動訓練
        task_id = training_service.start_training(
            model_name=model_name,
            data_file_id=data_file_id,
            prediction_days=prediction_days,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "訓練任務已啟動",
                    "data": {"taskId": task_id},
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"啟動訓練失敗: {str(e)}"}), 500


@training_bp.route("/training/tasks/<task_id>", methods=["GET"])
def get_training_task(task_id):
    """取得訓練任務進度"""
    try:
        task = training_service.get_training_task(task_id)

        if not task:
            return jsonify({"success": False, "error": "找不到訓練任務"}), 404

        return jsonify({"success": True, "data": task.to_dict()}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"取得任務失敗: {str(e)}"}), 500


@training_bp.route("/training/tasks", methods=["GET"])
def list_training_tasks():
    """列出所有訓練任務"""
    try:
        tasks = training_service.list_training_tasks()
        tasks_data = [task.to_dict() for task in tasks]

        return jsonify({"success": True, "data": tasks_data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"列出任務失敗: {str(e)}"}), 500
