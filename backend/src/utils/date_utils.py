"""
日期處理工具模組
提供日期解析、格式轉換、範圍驗證等工具函式
"""
from datetime import datetime, date
from typing import Optional, Union
import pandas as pd


def parse_date(date_str: str) -> Optional[date]:
    """
    解析日期字串，支援多種格式

    支援格式:
        - YYYY/M/D (例如: 2025/1/1)
        - YYYY-MM-DD (例如: 2025-01-01)
        - YYYY/MM/DD (例如: 2025/01/01)

    參數:
        date_str: 日期字串

    回傳:
        datetime.date 物件，若解析失敗則回傳 None
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # 嘗試常見的日期格式
    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y/%#m/%#d",  # Windows 格式（無前綴 0）
        "%Y-%#m-%#d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    # 嘗試使用 pandas 解析（更寬鬆）
    try:
        parsed = pd.to_datetime(date_str, format="mixed")
        return parsed.date()
    except Exception:
        return None


def format_date_iso(dt: Union[date, datetime]) -> str:
    """
    格式化日期為 ISO 8601 格式 (YYYY-MM-DD)

    參數:
        dt: datetime.date 或 datetime.datetime 物件

    回傳:
        ISO 8601 格式的日期字串
    """
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    return dt.isoformat()


def format_datetime_iso(dt: datetime) -> str:
    """
    格式化日期時間為 ISO 8601 格式 (YYYY-MM-DDTHH:MM:SS)

    參數:
        dt: datetime.datetime 物件

    回傳:
        ISO 8601 格式的日期時間字串
    """
    return dt.isoformat()


def is_date_in_range(
    target_date: date, start_date: date, end_date: date
) -> bool:
    """
    檢查日期是否在指定範圍內（包含起始與結束日期）

    參數:
        target_date: 目標日期
        start_date: 起始日期
        end_date: 結束日期

    回傳:
        True 若日期在範圍內，否則 False
    """
    return start_date <= target_date <= end_date


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    驗證日期範圍是否有效（起始日期 <= 結束日期）

    參數:
        start_date: 起始日期
        end_date: 結束日期

    回傳:
        True 若範圍有效，否則 False
    """
    return start_date <= end_date


def get_current_datetime_iso() -> str:
    """
    取得當前日期時間的 ISO 8601 格式字串

    回傳:
        ISO 8601 格式的當前日期時間字串
    """
    return datetime.now().isoformat()


def parse_iso_datetime(iso_str: str) -> Optional[datetime]:
    """
    解析 ISO 8601 格式的日期時間字串

    參數:
        iso_str: ISO 8601 格式的日期時間字串

    回傳:
        datetime 物件，若解析失敗則回傳 None
    """
    try:
        return datetime.fromisoformat(iso_str)
    except Exception:
        return None
