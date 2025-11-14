"""
模型比較 API 路由
處理模型效能比較請求
"""
from flask import Blueprint, request, jsonify
from services.comparison_service import get_comparison_service

comparison_bp = Blueprint("comparison", __name__)
comparison_service = get_comparison_service()


@comparison_bp.route("/compare", methods=["POST"])
def compare_models():
    """比較多個模型"""
    try:
        data = request.get_json()

        # 驗證必要欄位
        if not data:
            return jsonify({"success": False, "error": "請求 body 不可為空"}), 400

        model_ids = data.get("modelIds")

        # 欄位驗證
        if not model_ids:
            return jsonify({"success": False, "error": "請選擇要比較的模型"}), 400

        if not isinstance(model_ids, list):
            return jsonify({"success": False, "error": "modelIds 必須是陣列"}), 400

        # 執行比較
        result = comparison_service.compare_models(model_ids)

        return jsonify({"success": True, "data": result.to_dict()}), 200

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"模型比較失敗: {str(e)}"}), 500
