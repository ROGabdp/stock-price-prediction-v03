"""
模型比較服務
提供多模型效能比較功能
"""
from typing import List

from services.model_service import get_model_service
from services.metadata_service import get_metadata_service
from models.comparison import ComparisonResult, ModelComparisonItem
from utils.date_utils import get_current_datetime_iso


class ComparisonService:
    """模型比較服務"""

    def __init__(self):
        self.model_service = get_model_service()
        self.metadata_service = get_metadata_service()

    def compare_models(self, model_ids: List[str]) -> ComparisonResult:
        """
        比較多個模型

        參數:
            model_ids: 模型 ID 列表

        回傳:
            ComparisonResult 物件

        拋出:
            ValueError: 若模型不存在或參數無效
        """
        # 驗證輸入
        if not model_ids or len(model_ids) < 2:
            raise ValueError("至少需要選擇 2 個模型進行比較")

        if len(model_ids) > 10:
            raise ValueError("最多只能同時比較 10 個模型")

        # 收集模型資訊
        comparison_items = []
        for model_id in model_ids:
            model_info = self.model_service.get_model(model_id)

            if not model_info:
                raise ValueError(f"找不到模型: {model_id}")

            if model_info.status != "ready":
                raise ValueError(f"模型 {model_info.model_name} 尚未完成訓練，無法比較")

            # 取得資料檔案資訊
            data_file = self.metadata_service.get_data_file(model_info.data_file_id)
            data_file_name = (
                data_file.get("originalFileName", "未知")
                if data_file
                else "未知"
            )

            # 建立比較項目
            item = ModelComparisonItem(
                model_id=model_info.model_id,
                model_name=model_info.model_name,
                prediction_days=model_info.prediction_days,
                trained_at=model_info.trained_at,
                hyperparameters=model_info.hyperparameters,
                metrics={
                    "trainLoss": model_info.metrics.train_loss,
                    "valLoss": model_info.metrics.val_loss,
                    "trainMAE": model_info.metrics.train_mae,
                    "valMAE": model_info.metrics.val_mae,
                },
                data_file_name=data_file_name,
                data_file_id=model_info.data_file_id,
            )
            comparison_items.append(item)

        # 找出最佳模型（根據 val_loss）
        best_model_item = min(comparison_items, key=lambda x: x.metrics["valLoss"])
        best_model_info = {
            "modelId": best_model_item.model_id,
            "modelName": best_model_item.model_name,
            "valLoss": best_model_item.metrics["valLoss"],
            "valMAE": best_model_item.metrics["valMAE"],
        }

        # 建立比較結果
        result = ComparisonResult(
            models=comparison_items,
            best_model=best_model_info,
            comparison_timestamp=get_current_datetime_iso(),
        )

        return result


# 全域單例
_comparison_service_instance = None


def get_comparison_service() -> ComparisonService:
    """取得比較服務單例"""
    global _comparison_service_instance
    if _comparison_service_instance is None:
        _comparison_service_instance = ComparisonService()
    return _comparison_service_instance
