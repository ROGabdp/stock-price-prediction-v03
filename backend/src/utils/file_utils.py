"""
檔案工具模組
提供檔案命名、UUID 產生、檔案操作等工具函式
"""
import uuid
import os
from pathlib import Path
from typing import Optional


def generate_file_id() -> str:
    """
    產生唯一的檔案 ID

    回傳:
        格式為 'file_' + UUID 的字串
    """
    return f"file_{uuid.uuid4().hex[:8]}"


def generate_model_id() -> str:
    """
    產生唯一的模型 ID

    回傳:
        格式為 'model_' + UUID 的字串
    """
    return f"model_{uuid.uuid4().hex[:8]}"


def generate_task_id() -> str:
    """
    產生唯一的訓練任務 ID

    回傳:
        格式為 'task_' + UUID 的字串
    """
    return f"task_{uuid.uuid4().hex[:8]}"


def create_safe_filename(file_id: str, original_filename: str) -> str:
    """
    建立安全的檔案名稱（UUID 前綴 + 原始檔名）

    參數:
        file_id: 檔案 ID
        original_filename: 原始檔案名稱

    回傳:
        安全的檔案名稱
    """
    # 移除路徑分隔符號，避免路徑穿越攻擊
    safe_name = original_filename.replace("/", "_").replace("\\", "_")
    return f"{file_id}_{safe_name}"


def delete_file_safe(file_path: Path) -> bool:
    """
    安全地刪除檔案

    參數:
        file_path: 檔案路徑

    回傳:
        True 若刪除成功，False 若檔案不存在或刪除失敗
    """
    try:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"刪除檔案失敗: {file_path}, 錯誤: {e}")
        return False


def get_file_size(file_path: Path) -> int:
    """
    取得檔案大小（位元組）

    參數:
        file_path: 檔案路徑

    回傳:
        檔案大小（位元組），若檔案不存在則回傳 0
    """
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.stat().st_size
        return 0
    except Exception:
        return 0


def ensure_parent_dir(file_path: Path) -> None:
    """
    確保檔案的父目錄存在

    參數:
        file_path: 檔案路徑
    """
    parent_dir = file_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
