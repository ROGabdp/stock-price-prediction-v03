"""
預測執行 API 路由
處理預測請求與結果回傳
"""
from flask import Blueprint, request, jsonify
from services.prediction_service import get_prediction_service

prediction_bp = Blueprint("prediction", __name__)
prediction_service = get_prediction_service()


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    """執行預測"""
    try:
        data = request.get_json()

        # 驗證必要欄位
        if not data:
            return jsonify({"success": False, "error": "請求 body 不可為空"}), 400

        model_id = data.get("modelId")
        data_file_id = data.get("dataFileId")
        start_date = data.get("startDate")

        # 欄位驗證
        if not model_id:
            return jsonify({"success": False, "error": "請選擇模型"}), 400

        if not data_file_id:
            return jsonify({"success": False, "error": "請選擇資料檔案"}), 400

        if not start_date:
            return jsonify({"success": False, "error": "請選擇預測起始日期"}), 400

        # 執行預測
        result = prediction_service.predict(
            model_id=model_id,
            data_file_id=data_file_id,
            start_date=start_date,
        )

        return jsonify({"success": True, "data": result.to_dict()}), 200

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"執行預測失敗: {str(e)}"}), 500
