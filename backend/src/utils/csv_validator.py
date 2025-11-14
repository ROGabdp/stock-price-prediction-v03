"""
CSV 驗證工具模組
提供 CSV 檔案格式驗證、必要欄位檢查、數值驗證等功能
"""
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import date

from config import REQUIRED_CSV_COLUMNS, MIN_DATA_ROWS, MAX_DATA_ROWS
from utils.date_utils import parse_date


class CSVValidationError(Exception):
    """CSV 驗證錯誤"""

    pass


def validate_csv_file(file_path: Path) -> Tuple[bool, List[str], Optional[pd.DataFrame]]:
    """
    驗證 CSV 檔案格式與內容

    參數:
        file_path: CSV 檔案路徑

    回傳:
        (是否通過驗證, 錯誤訊息列表, DataFrame)
        若驗證失敗，DataFrame 為 None
    """
    errors = []

    # 檢查檔案是否存在
    if not file_path.exists() or not file_path.is_file():
        return False, ["檔案不存在"], None

    try:
        # 嘗試讀取 CSV
        df = pd.read_csv(file_path)
    except Exception as e:
        return False, [f"無法讀取 CSV 檔案: {str(e)}"], None

    # 1. 檢查必要欄位
    missing_columns = check_required_columns(df)
    if missing_columns:
        errors.append(
            f"缺少必要欄位: {', '.join(missing_columns)}。"
            f"必要欄位包含: {', '.join(REQUIRED_CSV_COLUMNS)}"
        )

    # 2. 檢查資料筆數
    row_count = len(df)
    if row_count < MIN_DATA_ROWS:
        errors.append(f"資料不足，至少需要 {MIN_DATA_ROWS} 筆資料，目前只有 {row_count} 筆")

    if row_count > MAX_DATA_ROWS:
        errors.append(
            f"資料過多，最多支援 {MAX_DATA_ROWS} 筆資料，目前有 {row_count} 筆"
        )

    # 若缺少必要欄位，無法繼續驗證
    if missing_columns:
        return False, errors, None

    # 3. 驗證日期欄位
    date_errors = validate_date_column(df)
    if date_errors:
        errors.extend(date_errors)

    # 4. 驗證數值欄位
    numeric_errors = validate_numeric_columns(df)
    if numeric_errors:
        errors.extend(numeric_errors)

    # 5. 驗證價格邏輯
    price_errors = validate_price_logic(df)
    if price_errors:
        errors.extend(price_errors)

    # 回傳結果
    if errors:
        return False, errors, None
    else:
        return True, [], df


def check_required_columns(df: pd.DataFrame) -> List[str]:
    """
    檢查必要欄位是否存在

    參數:
        df: pandas DataFrame

    回傳:
        缺少的欄位列表
    """
    existing_columns = df.columns.tolist()
    missing = [col for col in REQUIRED_CSV_COLUMNS if col not in existing_columns]
    return missing


def validate_date_column(df: pd.DataFrame) -> List[str]:
    """
    驗證日期欄位格式與有效性

    參數:
        df: pandas DataFrame

    回傳:
        錯誤訊息列表
    """
    errors = []

    # 檢查日期欄位是否有空值
    if df["date"].isnull().any():
        null_count = df["date"].isnull().sum()
        errors.append(f"日期欄位包含 {null_count} 個空值")

    # 嘗試解析日期
    invalid_dates = []
    for idx, date_str in enumerate(df["date"]):
        if pd.isnull(date_str):
            continue
        parsed = parse_date(str(date_str))
        if parsed is None:
            invalid_dates.append((idx + 1, date_str))

    if invalid_dates:
        # 只顯示前 5 個錯誤
        sample_errors = invalid_dates[:5]
        error_msg = "日期格式錯誤，無法解析以下日期: " + ", ".join(
            [f"第 {row} 列: '{val}'" for row, val in sample_errors]
        )
        if len(invalid_dates) > 5:
            error_msg += f" (共 {len(invalid_dates)} 個錯誤)"
        errors.append(error_msg)

    # 檢查日期重複
    if not df["date"].isnull().all():
        duplicates = df["date"].duplicated().sum()
        if duplicates > 0:
            errors.append(f"發現 {duplicates} 個重複的日期")

    return errors


def validate_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    驗證數值欄位（價格與成交量）

    參數:
        df: pandas DataFrame

    回傳:
        錯誤訊息列表
    """
    errors = []
    numeric_cols = ["open", "high", "low", "close", "volume"]

    for col in numeric_cols:
        # 檢查是否為數值型態
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                errors.append(f"{col} 欄位包含無法轉換為數值的資料")
                continue

        # 檢查空值
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"{col} 欄位包含 {null_count} 個空值或無效數值")

        # 檢查負數（價格與成交量不可為負）
        if col == "volume":
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                errors.append(f"{col} 欄位包含 {negative_count} 個負數值")
        else:  # 價格欄位
            non_positive_count = (df[col] <= 0).sum()
            if non_positive_count > 0:
                errors.append(f"{col} 欄位包含 {non_positive_count} 個非正數值（價格必須大於 0）")

    return errors


def validate_price_logic(df: pd.DataFrame) -> List[str]:
    """
    驗證價格邏輯關係（最高價 >= 最低價）

    參數:
        df: pandas DataFrame

    回傳:
        錯誤訊息列表
    """
    errors = []

    # 檢查 high >= low
    invalid_rows = df[df["high"] < df["low"]]
    if len(invalid_rows) > 0:
        errors.append(
            f"發現 {len(invalid_rows)} 筆資料的最高價低於最低價，"
            f"例如第 {invalid_rows.index[0] + 1} 列"
        )

    return errors


def get_date_range(df: pd.DataFrame) -> Tuple[Optional[date], Optional[date]]:
    """
    取得資料的日期範圍

    參數:
        df: pandas DataFrame

    回傳:
        (起始日期, 結束日期)，若無法解析則回傳 (None, None)
    """
    try:
        dates = []
        for date_str in df["date"]:
            if pd.isnull(date_str):
                continue
            parsed = parse_date(str(date_str))
            if parsed:
                dates.append(parsed)

        if not dates:
            return None, None

        return min(dates), max(dates)
    except Exception:
        return None, None
