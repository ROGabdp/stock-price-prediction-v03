"""
資料管理服務
處理 CSV 檔案上傳、驗證、儲存、刪除
"""
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import DATA_DIR
from utils.file_utils import generate_file_id, create_safe_filename, delete_file_safe
from utils.csv_validator import validate_csv_file, get_date_range
from utils.date_utils import get_current_datetime_iso, format_date_iso
from services.metadata_service import get_metadata_service
from models.data_file import DataFile, DateRange


class DataService:
    """資料管理服務"""

    def __init__(self):
        self.metadata_service = get_metadata_service()
        self.data_dir = DATA_DIR

        # 確保資料目錄存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def upload_csv_file(
        self,
        file_content: bytes,
        original_filename: str,
    ) -> DataFile:
        """
        上傳並驗證 CSV 檔案

        參數:
            file_content: 檔案內容（bytes）
            original_filename: 原始檔案名稱

        回傳:
            DataFile 物件

        拋出:
            ValueError: 若驗證失敗
        """
        # 邊界情況檢查：檔案大小限制 (100MB)
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(
                f"檔案大小超過限制。檔案大小: {len(file_content) / 1024 / 1024:.2f}MB，"
                f"最大允許: 100MB"
            )

        # 邊界情況檢查：檔案內容不可為空
        if len(file_content) == 0:
            raise ValueError("檔案內容不可為空")

        # 1. 生成檔案 ID 與安全檔名
        file_id = generate_file_id()
        safe_filename = create_safe_filename(file_id, original_filename)
        file_path = self.data_dir / safe_filename

        # 2. 將檔案暫時寫入磁碟
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(file_content)

        try:
            # 3. 驗證 CSV 格式與內容
            is_valid, errors, df = validate_csv_file(temp_path)

            if not is_valid:
                # 刪除臨時檔案
                temp_path.unlink()
                raise ValueError(f"CSV 驗證失敗: {'; '.join(errors)}")

            # 4. 移動到正式位置
            shutil.move(str(temp_path), str(file_path))

            # 5. 取得日期範圍
            start_date, end_date = get_date_range(df)
            if not start_date or not end_date:
                raise ValueError("無法解析日期範圍")

            date_range = DateRange(
                start=format_date_iso(start_date),
                end=format_date_iso(end_date),
            )

            # 6. 建立 DataFile 物件
            data_file = DataFile(
                file_id=file_id,
                file_name=safe_filename,
                original_file_name=original_filename,
                file_path=str(file_path),
                uploaded_at=get_current_datetime_iso(),
                date_range=date_range,
                row_count=len(df),
                columns=list(df.columns),
                file_size_bytes=file_path.stat().st_size,
                status="valid",
                validation_errors=[],
            )

            # 7. 儲存 metadata
            self.metadata_service.add_data_file(data_file.to_dict())

            return data_file

        except Exception as e:
            # 清理臨時檔案
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def list_data_files(self) -> List[Dict[str, Any]]:
        """
        列出所有資料檔案

        回傳:
            資料檔案列表（字典格式）
        """
        data_files = self.metadata_service.list_data_files()
        # 過濾掉已刪除的檔案
        return [df for df in data_files if df.get("status") != "deleted"]

    def get_data_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        取得單一資料檔案資訊

        參數:
            file_id: 檔案 ID

        回傳:
            資料檔案字典，若不存在則回傳 None
        """
        return self.metadata_service.get_data_file(file_id)

    def delete_data_file(self, file_id: str) -> None:
        """
        刪除資料檔案

        參數:
            file_id: 檔案 ID

        拋出:
            ValueError: 若檔案不存在或無法刪除
        """
        data_file_dict = self.metadata_service.get_data_file(file_id)

        if not data_file_dict:
            raise ValueError(f"找不到資料檔案: {file_id}")

        # 檢查是否已被模型使用
        models = self.metadata_service.list_models()
        for model in models:
            if model.get("dataFileId") == file_id:
                raise ValueError(
                    f"資料檔案正被模型 {model.get('modelName')} 使用，無法刪除"
                )

        # 刪除實體檔案
        file_path = Path(data_file_dict["filePath"])
        delete_file_safe(file_path)

        # 更新 metadata 狀態
        self.metadata_service.update_data_file_status(file_id, "deleted")


# 全域單例
_data_service_instance = None


def get_data_service() -> DataService:
    """取得資料服務單例"""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance
