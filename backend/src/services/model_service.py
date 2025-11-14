"""
模型服務
提供模型 CRUD、載入模型、刪除模型邏輯
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
from tensorflow.keras.models import load_model

from config import MODELS_DIR
from services.metadata_service import get_metadata_service
from models.prediction_model import PredictionModel
from utils.file_utils import delete_file_safe


class ModelService:
    """模型服務"""

    def __init__(self):
        self.metadata_service = get_metadata_service()

    def get_model(self, model_id: str) -> Optional[PredictionModel]:
        """
        取得模型資訊

        參數:
            model_id: 模型 ID

        回傳:
            PredictionModel 物件，若不存在則回傳 None
        """
        model_data = self.metadata_service.get_model(model_id)
        if model_data:
            return PredictionModel.from_dict(model_data)
        return None

    def list_models(self, include_deleted: bool = False) -> List[PredictionModel]:
        """
        列出所有模型

        參數:
            include_deleted: 是否包含已刪除的模型

        回傳:
            PredictionModel 列表
        """
        models_data = self.metadata_service.list_models(include_deleted)
        return [PredictionModel.from_dict(m) for m in models_data]

    def load_keras_model(self, model_id: str):
        """
        載入 Keras 模型

        參數:
            model_id: 模型 ID

        回傳:
            Keras 模型物件

        拋出:
            FileNotFoundError: 若模型檔案不存在
            ValueError: 若模型資訊不存在
        """
        model_info = self.get_model(model_id)
        if not model_info:
            raise ValueError(f"找不到模型: {model_id}")

        model_path = Path(model_info.model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"模型檔案不存在: {model_path}")

        return load_model(str(model_path))

    def delete_model(self, model_id: str, delete_file: bool = True) -> bool:
        """
        刪除模型（軟刪除元資料，可選刪除檔案）

        參數:
            model_id: 模型 ID
            delete_file: 是否同時刪除模型檔案

        回傳:
            True 若刪除成功，False 若模型不存在
        """
        model_info = self.get_model(model_id)
        if not model_info:
            return False

        # 軟刪除元資料
        success = self.metadata_service.delete_model(model_id, soft_delete=True)

        # 刪除模型檔案（若需要）
        if success and delete_file:
            model_path = Path(model_info.model_path)
            delete_file_safe(model_path)

        return success

    def add_model(self, model: PredictionModel) -> None:
        """
        新增模型元資料

        參數:
            model: PredictionModel 物件
        """
        self.metadata_service.add_model(model.to_dict())

    def update_model(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新模型元資料

        參數:
            model_id: 模型 ID
            updates: 要更新的欄位

        回傳:
            True 若更新成功，False 若模型不存在
        """
        return self.metadata_service.update_model(model_id, updates)


# 全域單例
_model_service_instance = None


def get_model_service() -> ModelService:
    """取得模型服務單例"""
    global _model_service_instance
    if _model_service_instance is None:
        _model_service_instance = ModelService()
    return _model_service_instance
