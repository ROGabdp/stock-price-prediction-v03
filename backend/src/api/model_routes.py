"""
模型管理 API 路由
處理模型的查詢、列表、刪除
"""
from flask import Blueprint, jsonify
from services.model_service import get_model_service

model_bp = Blueprint("models", __name__)
model_service = get_model_service()


@model_bp.route("", methods=["GET"])
@model_bp.route("/", methods=["GET"])
def list_models():
    """列出所有模型"""
    try:
        models = model_service.list_models(include_deleted=False)
        models_data = [model.to_dict() for model in models]

        return jsonify({"success": True, "data": models_data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"列出模型失敗: {str(e)}"}), 500


@model_bp.route("/<model_id>", methods=["GET"])
def get_model(model_id):
    """取得模型詳情"""
    try:
        model = model_service.get_model(model_id)

        if not model:
            return jsonify({"success": False, "error": "找不到指定的模型"}), 404

        return jsonify({"success": True, "data": model.to_dict()}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"取得模型失敗: {str(e)}"}), 500


@model_bp.route("/<model_id>", methods=["DELETE"])
def delete_model(model_id):
    """刪除模型"""
    try:
        success = model_service.delete_model(model_id, delete_file=True)

        if not success:
            return jsonify({"success": False, "error": "找不到指定的模型"}), 404

        return (
            jsonify({"success": True, "message": "模型已刪除"}),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"刪除模型失敗: {str(e)}"}), 500
