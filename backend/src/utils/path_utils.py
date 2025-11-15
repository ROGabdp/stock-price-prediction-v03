"""
路徑工具函式
處理跨平台路徑轉換（Windows / WSL2）
"""
import os
import re
from pathlib import Path


def convert_to_native_path(path_str: str) -> str:
    """
    將路徑轉換為當前平台的原生格式

    如果在 WSL2 環境中運行，將 Windows 路徑轉換為 WSL2 路徑
    如果在 Windows 環境中運行，保持 Windows 路徑格式

    參數:
        path_str: 原始路徑字串

    回傳:
        轉換後的路徑字串

    範例:
        WSL2 環境：
            D:\\data\\file.csv -> /mnt/d/data/file.csv
        Windows 環境：
            D:\\data\\file.csv -> D:\\data\\file.csv
    """
    # 檢查是否在 WSL2 環境中
    is_wsl = os.getcwd().startswith('/mnt/')

    # 檢查是否為 Windows 路徑格式 (例如 D:\path 或 D:/path)
    windows_path_pattern = r'^([A-Z]):[/\\]'
    match = re.match(windows_path_pattern, path_str, re.IGNORECASE)

    if is_wsl and match:
        # 在 WSL2 中，將 Windows 路徑轉換為 /mnt/x/ 格式
        drive_letter = match.group(1).lower()
        # 移除磁碟機代號和冒號 (D:)，保留後續路徑
        path_without_drive = path_str[2:].lstrip('/\\')
        # 統一使用正斜線
        path_without_drive = path_without_drive.replace('\\', '/')
        return f'/mnt/{drive_letter}/{path_without_drive}'

    # 如果不在 WSL2 或不是 Windows 路徑，保持原樣
    return path_str


def get_absolute_path(path_str: str) -> Path:
    """
    取得絕對路徑，自動處理跨平台轉換

    參數:
        path_str: 原始路徑字串

    回傳:
        Path 物件（絕對路徑）
    """
    native_path = convert_to_native_path(path_str)
    return Path(native_path).absolute()
