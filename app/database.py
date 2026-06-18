import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from app.config import config as app_config

logger = logging.getLogger(__name__)


class Database:
    """SQLite 数据库管理类 - 管理数据库连接和表结构"""

    _instance: Optional["Database"] = None
    _connection: sqlite3.Connection | None = None

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_db_dir()

    def _ensure_db_dir(self) -> None:
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls, db_path: str | None = None) -> "Database":
        if cls._instance is None:
            if db_path is None:
                db_path = app_config.db_path
            cls._instance = cls(db_path)
        return cls._instance

    @property
    def connection(self) -> sqlite3.Connection:
        """获取数据库连接（懒加载，单例级别复用）"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        if cls._connection is not None:
            cls._connection.close()
        cls._instance = None
        cls._connection = None

    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_cursor(self) -> Any:
        """获取数据库游标的上下文管理器"""
        conn = self.connection
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def init_schema(self) -> None:
        """初始化数据库表结构"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    icon TEXT,
                    display_order INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    icon TEXT DEFAULT 'fas fa-link',
                    display_order INTEGER DEFAULT 0,
                    visit_count INTEGER DEFAULT 0,
                    last_visit INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_category
                ON items(category_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_visit_count
                ON items(visit_count DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_url
                ON items(url)
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            logger.info("Database schema initialized")


def get_db() -> Database:
    """获取数据库实例的便捷函数"""
    return Database.get_instance()


def init_db() -> None:
    """初始化数据库"""
    db = get_db()
    db.init_schema()
