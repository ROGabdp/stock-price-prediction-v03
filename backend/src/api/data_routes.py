"""
資料管理 API 路由
處理檔案上傳、列表、刪除
"""
from flask import Blueprint, request, jsonify
from services.data_service import get_data_service

data_bp = Blueprint("data", __name__)
data_service = get_data_service()


@data_bp.route("/files", methods=["GET"])
def list_data_files():
    """列出所有資料檔案"""
    try:
        data_files = data_service.list_data_files()
        return jsonify({"success": True, "data": data_files}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"取得資料檔案列表失敗: {str(e)}"}), 500


@data_bp.route("/files/<file_id>", methods=["GET"])
def get_data_file(file_id):
    """取得單一資料檔案資訊"""
    try:
        data_file = data_service.get_data_file(file_id)

        if not data_file:
            return jsonify({"success": False, "error": "找不到資料檔案"}), 404

        return jsonify({"success": True, "data": data_file}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"取得資料檔案失敗: {str(e)}"}), 500


@data_bp.route("/upload", methods=["POST"])
def upload_csv_file():
    """上傳 CSV 檔案"""
    try:
        # 檢查是否有檔案
        if "file" not in request.files:
            return jsonify({"success": False, "error": "請選擇檔案"}), 400

        file = request.files["file"]

        # 檢查檔案名稱
        if file.filename == "":
            return jsonify({"success": False, "error": "檔案名稱不可為空"}), 400

        # 檢查副檔名
        if not file.filename.endswith(".csv"):
            return jsonify({"success": False, "error": "請上傳 CSV 檔案"}), 400

        # 讀取檔案內容
        file_content = file.read()

        if len(file_content) == 0:
            return jsonify({"success": False, "error": "檔案內容不可為空"}), 400

        # 上傳並驗證
        data_file = data_service.upload_csv_file(
            file_content=file_content,
            original_filename=file.filename,
        )

        return jsonify({"success": True, "data": data_file.to_dict()}), 201

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"上傳失敗: {str(e)}"}), 500


@data_bp.route("/files/<file_id>", methods=["DELETE"])
def delete_data_file(file_id):
    """刪除資料檔案"""
    try:
        data_service.delete_data_file(file_id)
        return jsonify({"success": True, "message": "資料檔案已刪除"}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"刪除失敗: {str(e)}"}), 500
