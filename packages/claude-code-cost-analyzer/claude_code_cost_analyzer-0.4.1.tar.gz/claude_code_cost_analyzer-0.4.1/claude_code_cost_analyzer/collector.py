"""ログファイル収集機能

Claude APIログファイルの探索と収集を行うモジュール。
指定されたディレクトリから再帰的にJSONログファイルを検索する。
"""

import os
from pathlib import Path
from typing import List, Union
import logging


logger = logging.getLogger(__name__)


def collect_log_files(directory: Union[str, Path]) -> List[Path]:
    """指定されたディレクトリからJSONログファイルを再帰的に収集する

    Args:
        directory: 検索対象のディレクトリパス

    Returns:
        見つかったJSONファイルのPathオブジェクトのリスト

    Raises:
        FileNotFoundError: 指定されたディレクトリが存在しない場合
        PermissionError: ディレクトリへのアクセス権限がない場合
        ValueError: 無効なパスが指定された場合
    """
    # パスオブジェクトに変換
    dir_path = Path(directory)

    # 基本バリデーション
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")

    # ディレクトリへのアクセス権限をチェック
    if not os.access(dir_path, os.R_OK):
        raise PermissionError(f"No read permission for directory: {dir_path}")

    try:
        # JSONファイルとJSONLファイルを再帰的に検索
        json_files = list(dir_path.rglob("*.json"))
        jsonl_files = list(dir_path.rglob("*.jsonl"))
        json_files.extend(jsonl_files)

        logger.info(f"Found {len(json_files)} JSON/JSONL files in {dir_path}")

        # ファイル修更時刻でソート（新しい順）
        json_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return json_files

    except PermissionError as e:
        logger.error(f"Permission denied while accessing {dir_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while collecting log files: {e}")
        raise
