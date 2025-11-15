"""
訓練服務
包含啟動訓練任務、監控進度、更新任務狀態
"""
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from config import MODELS_DIR, UPLOADED_DATA_DIR
from services.metadata_service import get_metadata_service
from services.model_service import get_model_service
from models.training_task import TrainingTask, TrainingProgress
from models.prediction_model import PredictionModel, ModelMetrics
from ml.trainer import ModelTrainer
from utils.file_utils import generate_task_id, generate_model_id, create_safe_filename
from utils.date_utils import get_current_datetime_iso
from utils.logger import log_training_start, log_training_complete, log_training_error


class TrainingService:
    """訓練服務"""

    def __init__(self):
        self.metadata_service = get_metadata_service()
        self.model_service = get_model_service()
        self.active_tasks: Dict[str, threading.Thread] = {}

    def start_training(
        self,
        model_name: str,
        data_file_id: str,
        prediction_days: int,
    ) -> str:
        """
        啟動訓練任務

        參數:
            model_name: 模型名稱
            data_file_id: 資料檔案 ID
            prediction_days: 預測天數

        回傳:
            訓練任務 ID

        拋出:
            ValueError: 若資料檔案不存在或無效
        """
        # 驗證資料檔案
        data_file = self.metadata_service.get_data_file(data_file_id)
        if not data_file:
            raise ValueError(f"找不到資料檔案: {data_file_id}")

        if data_file.get("status") != "valid":
            raise ValueError("資料檔案狀態無效，無法訓練模型")

        # 建立訓練任務
        task_id = generate_task_id()
        task = TrainingTask(
            task_id=task_id,
            model_name=model_name,
            data_file_id=data_file_id,
            prediction_days=prediction_days,
            status="pending",
            started_at=get_current_datetime_iso(),
        )

        # 儲存任務元資料
        self.metadata_service.add_training_task(task.to_dict())

        # 在背景執行緒啟動訓練
        training_thread = threading.Thread(
            target=self._execute_training,
            args=(task_id, model_name, data_file_id, prediction_days),
            daemon=True,
        )
        training_thread.start()
        self.active_tasks[task_id] = training_thread

        return task_id

    def _execute_training(
        self,
        task_id: str,
        model_name: str,
        data_file_id: str,
        prediction_days: int,
    ) -> None:
        """
        執行訓練（在背景執行緒中）

        參數:
            task_id: 訓練任務 ID
            model_name: 模型名稱
            data_file_id: 資料檔案 ID
            prediction_days: 預測天數
        """
        try:
            # 更新任務狀態為 running
            self.metadata_service.update_training_task(
                task_id, {"status": "running"}
            )

            # 取得資料檔案路徑
            data_file = self.metadata_service.get_data_file(data_file_id)
            file_path_str = data_file["filePath"]

            # WSL2 路徑轉換：如果是 Windows 路徑 (D:\...) 且工作目錄是 WSL (/mnt/...)
            import os
            import re
            if re.match(r'^[A-Z]:\\', file_path_str) and os.getcwd().startswith('/mnt/'):
                # 將 Windows 路徑轉換為 WSL2 路徑
                # D:\path\to\file -> /mnt/d/path/to/file
                drive_letter = file_path_str[0].lower()
                path_without_drive = file_path_str[3:].replace('\\', '/')
                file_path_str = f'/mnt/{drive_letter}/{path_without_drive}'

            data_file_path = Path(file_path_str).absolute()

            # 防禦性檢查：確保檔案存在
            if not data_file_path.exists():
                raise FileNotFoundError(
                    f"資料檔案不存在: {data_file_path}\n"
                    f"工作目錄: {Path.cwd()}\n"
                    f"原始路徑: {data_file['filePath']}\n"
                    f"轉換後路徑: {file_path_str}"
                )

            # 建立訓練器
            trainer = ModelTrainer(
                data_file_path=data_file_path,
                use_hyperparameter_tuning=True,
            )

            # 進度回調函式
            def progress_callback(epoch: int, logs: dict):
                progress = TrainingProgress(
                    current_epoch=epoch,
                    total_epochs=50,  # 假設最大 50 epochs
                    current_loss=float(logs.get("loss", 0)),
                    current_val_loss=float(logs.get("val_loss", 0)),
                )
                self.metadata_service.update_training_task(
                    task_id, {"progress": progress.to_dict()}
                )

            # 記錄訓練開始
            log_training_start(
                model_name=model_name,
                data_file_id=data_file_id,
                prediction_days=prediction_days,
                hyperparameters={
                    "epochs": 50,
                    "batch_size": 32,
                    "use_hyperparameter_tuning": True,
                },
            )

            # 執行訓練
            result = trainer.train(
                epochs=50,
                batch_size=32,
                progress_callback=progress_callback,
            )

            # 儲存模型
            model_id = generate_model_id()
            model_filename = create_safe_filename(model_id, f"{model_name}.keras")
            model_path = MODELS_DIR / model_filename
            trainer.save_model(model_path)

            # 建立模型元資料
            model = PredictionModel(
                model_id=model_id,
                model_name=model_name,
                model_path=str(model_path),
                trained_at=get_current_datetime_iso(),
                training_duration=result["trainingDuration"],
                data_file_id=data_file_id,
                data_file_name=data_file["fileName"],
                prediction_days=prediction_days,
                metrics=ModelMetrics.from_dict(result["metrics"]),
                hyperparameters=result["hyperparameters"],
                training_task_id=task_id,
                status="ready",
            )

            # 儲存模型元資料
            self.model_service.add_model(model)

            # 記錄訓練完成
            log_training_complete(
                model_name=model_name,
                model_id=model_id,
                train_loss=model.metrics.train_loss,
                val_loss=model.metrics.val_loss,
                train_mae=model.metrics.train_mae,
                val_mae=model.metrics.val_mae,
                execution_time=result["trainingDuration"],
            )

            # 更新訓練任務為完成
            self.metadata_service.update_training_task(
                task_id,
                {
                    "status": "completed",
                    "completedAt": get_current_datetime_iso(),
                    "duration": result["trainingDuration"],
                    "resultModelId": model_id,
                },
            )

        except Exception as e:
            # 訓練失敗
            import traceback
            error_message = str(e)
            stack_trace = traceback.format_exc()

            # 記錄訓練錯誤（包含堆疊追蹤）
            log_training_error(model_name=model_name, error_message=f"{error_message}\n堆疊追蹤:\n{stack_trace}")

            self.metadata_service.update_training_task(
                task_id,
                {
                    "status": "failed",
                    "completedAt": get_current_datetime_iso(),
                    "error": error_message,
                },
            )

        finally:
            # 移除活動任務
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

    def get_training_task(self, task_id: str) -> Optional[TrainingTask]:
        """
        取得訓練任務

        參數:
            task_id: 任務 ID

        回傳:
            TrainingTask 物件，若不存在則回傳 None
        """
        task_data = self.metadata_service.get_training_task(task_id)
        if task_data:
            return TrainingTask.from_dict(task_data)
        return None

    def list_training_tasks(self) -> list:
        """列出所有訓練任務"""
        tasks_data = self.metadata_service.list_training_tasks()
        return [TrainingTask.from_dict(t) for t in tasks_data]


# 全域單例
_training_service_instance = None


def get_training_service() -> TrainingService:
    """取得訓練服務單例"""
    global _training_service_instance
    if _training_service_instance is None:
        _training_service_instance = TrainingService()
    return _training_service_instance
