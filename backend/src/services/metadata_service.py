"""
元資料管理服務
提供 JSON 元資料的讀寫、原子操作、CRUD 方法
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from config import METADATA_FILE
from utils.date_utils import get_current_datetime_iso


class MetadataService:
    """元資料管理服務類別"""

    def __init__(self, metadata_file: Path = METADATA_FILE):
        self.metadata_file = metadata_file
        self._lock = threading.Lock()  # 執行緒鎖，確保原子操作
        self._ensure_metadata_file()

    def _ensure_metadata_file(self) -> None:
        """確保元資料檔案存在，若不存在則建立"""
        if not self.metadata_file.exists():
            self._initialize_metadata()

    def _initialize_metadata(self) -> None:
        """初始化元資料檔案"""
        initial_data = {
            "version": "1.0",
            "lastUpdated": get_current_datetime_iso(),
            "dataFiles": [],
            "models": [],
            "trainingTasks": [],
        }
        self._write_metadata(initial_data)

    def _read_metadata(self) -> Dict[str, Any]:
        """
        讀取元資料

        回傳:
            元資料字典
        """
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self._initialize_metadata()
            return self._read_metadata()
        except json.JSONDecodeError:
            # 檔案損毀，重新初始化
            print(f"警告: 元資料檔案損毀，重新初始化")
            self._initialize_metadata()
            return self._read_metadata()

    def _write_metadata(self, data: Dict[str, Any]) -> None:
        """
        原子性寫入元資料（先寫入臨時檔案再重新命名）

        參數:
            data: 元資料字典
        """
        # 更新 lastUpdated
        data["lastUpdated"] = get_current_datetime_iso()

        # 寫入臨時檔案
        temp_file = self.metadata_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 原子性重新命名
        shutil.move(str(temp_file), str(self.metadata_file))

    # ==================== 資料檔案 CRUD ====================

    def add_data_file(self, data_file: Dict[str, Any]) -> None:
        """
        新增資料檔案元資料

        參數:
            data_file: 資料檔案字典
        """
        with self._lock:
            metadata = self._read_metadata()
            metadata["dataFiles"].append(data_file)
            self._write_metadata(metadata)

    def get_data_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        取得資料檔案元資料

        參數:
            file_id: 檔案 ID

        回傳:
            資料檔案字典，若不存在則回傳 None
        """
        metadata = self._read_metadata()
        for data_file in metadata["dataFiles"]:
            if data_file["fileId"] == file_id:
                return data_file
        return None

    def list_data_files(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有資料檔案

        參數:
            include_deleted: 是否包含已刪除的檔案

        回傳:
            資料檔案列表
        """
        metadata = self._read_metadata()
        data_files = metadata["dataFiles"]

        if not include_deleted:
            data_files = [f for f in data_files if f.get("status") != "deleted"]

        return data_files

    def update_data_file(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新資料檔案元資料

        參數:
            file_id: 檔案 ID
            updates: 要更新的欄位字典

        回傳:
            True 若更新成功，False 若檔案不存在
        """
        with self._lock:
            metadata = self._read_metadata()
            for data_file in metadata["dataFiles"]:
                if data_file["fileId"] == file_id:
                    data_file.update(updates)
                    self._write_metadata(metadata)
                    return True
            return False

    def update_data_file_status(self, file_id: str, status: str) -> bool:
        """
        更新資料檔案狀態

        參數:
            file_id: 檔案 ID
            status: 新狀態 (valid, invalid, deleted)

        回傳:
            True 若更新成功，False 若檔案不存在
        """
        return self.update_data_file(file_id, {"status": status})

    def delete_data_file(self, file_id: str, soft_delete: bool = True) -> bool:
        """
        刪除資料檔案（軟刪除或硬刪除）

        參數:
            file_id: 檔案 ID
            soft_delete: True 為軟刪除（更新狀態），False 為硬刪除（移除記錄）

        回傳:
            True 若刪除成功，False 若檔案不存在
        """
        with self._lock:
            metadata = self._read_metadata()

            if soft_delete:
                # 軟刪除：更新狀態
                for data_file in metadata["dataFiles"]:
                    if data_file["fileId"] == file_id:
                        data_file["status"] = "deleted"
                        self._write_metadata(metadata)
                        return True
                return False
            else:
                # 硬刪除：移除記錄
                original_count = len(metadata["dataFiles"])
                metadata["dataFiles"] = [
                    f for f in metadata["dataFiles"] if f["fileId"] != file_id
                ]
                if len(metadata["dataFiles"]) < original_count:
                    self._write_metadata(metadata)
                    return True
                return False

    # ==================== 模型 CRUD ====================

    def add_model(self, model: Dict[str, Any]) -> None:
        """新增模型元資料"""
        with self._lock:
            metadata = self._read_metadata()
            metadata["models"].append(model)
            self._write_metadata(metadata)

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """取得模型元資料"""
        metadata = self._read_metadata()
        for model in metadata["models"]:
            if model["modelId"] == model_id:
                return model
        return None

    def list_models(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """列出所有模型"""
        metadata = self._read_metadata()
        models = metadata["models"]

        if not include_deleted:
            models = [m for m in models if m.get("status") != "deleted"]

        return models

    def update_model(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """更新模型元資料"""
        with self._lock:
            metadata = self._read_metadata()
            for model in metadata["models"]:
                if model["modelId"] == model_id:
                    model.update(updates)
                    self._write_metadata(metadata)
                    return True
            return False

    def delete_model(self, model_id: str, soft_delete: bool = True) -> bool:
        """刪除模型（軟刪除或硬刪除）"""
        with self._lock:
            metadata = self._read_metadata()

            if soft_delete:
                for model in metadata["models"]:
                    if model["modelId"] == model_id:
                        model["status"] = "deleted"
                        self._write_metadata(metadata)
                        return True
                return False
            else:
                original_count = len(metadata["models"])
                metadata["models"] = [
                    m for m in metadata["models"] if m["modelId"] != model_id
                ]
                if len(metadata["models"]) < original_count:
                    self._write_metadata(metadata)
                    return True
                return False

    # ==================== 訓練任務 CRUD ====================

    def add_training_task(self, task: Dict[str, Any]) -> None:
        """新增訓練任務元資料"""
        with self._lock:
            metadata = self._read_metadata()
            metadata["trainingTasks"].append(task)
            self._write_metadata(metadata)

    def get_training_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """取得訓練任務元資料"""
        metadata = self._read_metadata()
        for task in metadata["trainingTasks"]:
            if task["taskId"] == task_id:
                return task
        return None

    def list_training_tasks(self) -> List[Dict[str, Any]]:
        """列出所有訓練任務"""
        metadata = self._read_metadata()
        return metadata["trainingTasks"]

    def update_training_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新訓練任務元資料"""
        with self._lock:
            metadata = self._read_metadata()
            for task in metadata["trainingTasks"]:
                if task["taskId"] == task_id:
                    task.update(updates)
                    self._write_metadata(metadata)
                    return True
            return False


# 全域單例實例
_metadata_service_instance = None


def get_metadata_service() -> MetadataService:
    """
    取得元資料服務的單例實例

    回傳:
        MetadataService 實例
    """
    global _metadata_service_instance
    if _metadata_service_instance is None:
        _metadata_service_instance = MetadataService()
    return _metadata_service_instance
