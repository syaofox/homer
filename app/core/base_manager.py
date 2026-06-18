"""
数据管理器抽象基类 - 已废弃（项目已迁移至 SQLite）

此类用于旧的 JSON 文件配置管理方案，目前已被 SQLite 数据库替代。
保留此文件仅用于向前兼容，新代码应直接使用 DbService。
"""

import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BaseManager(ABC):
    """数据管理器抽象基类 - 提供通用缓存和文件操作（已废弃）"""

    def __init__(self, file_path: Path, cache_ttl: int = 30) -> None:
        self.file_path = file_path
        self._lock = threading.RLock()
        self._cache: dict[str, Any] | None = None
        self._cache_time: float = 0
        self._cache_ttl = cache_ttl
        self._ensure_parent_dir()

    def _ensure_parent_dir(self) -> None:
        parent = self.file_path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)

    def _is_cache_valid(self) -> bool:
        return (
            self._cache is not None and time.time() - self._cache_time < self._cache_ttl
        )

    def load(self, use_cache: bool = True) -> dict[str, Any]:
        with self._lock:
            if use_cache and self._is_cache_valid():
                return self._cache.copy()  # type: ignore[union-attr]

            try:
                if not self.file_path.exists():
                    default_data = self._get_default_data()
                    self._save_internal(default_data)
                    return default_data

                with open(self.file_path, encoding="utf-8") as f:
                    data = json.load(f)

                self._cache = data.copy()
                self._cache_time = time.time()
                return data  # type: ignore[no-any-return]

            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {self.file_path}, {e}")
                return self._get_default_data()
            except Exception as e:
                logger.error(f"加载文件失败: {self.file_path}, {e}")
                return self._get_default_data()

    def _save_internal(self, data: dict[str, Any]) -> None:
        temp_path = self.file_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path.replace(self.file_path)
            self._cache = data.copy()
            self._cache_time = time.time()
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"保存文件失败: {self.file_path}, {e}")
            raise

    def save(self, data: dict[str, Any]) -> None:
        with self._lock:
            self._save_internal(data)

    def update(self, updater_func: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        with self._lock:
            data = self.load(use_cache=False)
            updated_data = updater_func(data)
            self._save_internal(updated_data)

    def invalidate_cache(self) -> None:
        with self._lock:
            self._cache = None
            self._cache_time = 0

    @abstractmethod
    def _get_default_data(self) -> dict[str, Any]:
        pass
