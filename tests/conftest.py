"""
pytest 共享 fixtures
"""
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.database import Database, get_db, init_db


@pytest.fixture(autouse=True)
def temp_db() -> Generator[Path]:
    """
    每个测试用例使用独立的临时数据库文件。
    自动清理，互不干扰。
    """
    tmpdir = Path(tempfile.mkdtemp())
    db_path = tmpdir / "test_homer.db"

    # 重置单例，确保测试使用临时数据库
    Database.reset_instance()

    # 保存原 db_path，设置测试路径
    from app.config import config
    orig_db_path = config.db_file
    config.db_file = db_path

    # 重新初始化数据库实例
    init_db()

    yield db_path

    # 清理
    config.db_file = orig_db_path
    Database.reset_instance()


@pytest.fixture
def app() -> Flask:
    """创建 Flask 测试应用实例"""
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["SERVER_NAME"] = "localhost"
    flask_app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    return flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Flask 测试客户端"""
    return app.test_client()


@pytest.fixture
def db() -> Database:
    """获取测试数据库实例"""
    return get_db()


@pytest.fixture
def sample_data(db: Database) -> None:
    """插入测试数据"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO categories (id, name, icon, display_order) VALUES (1, '测试分类', 'fas fa-folder', 0)"  # noqa: E501
        )
        cursor.execute(
            "INSERT INTO items (id, category_id, title, url, icon, display_order, visit_count) VALUES "  # noqa: E501
            "(1, 1, '测试项目', 'https://example.com', 'fas fa-link', 0, 5)"
        )
        cursor.execute(
            "INSERT INTO items (id, category_id, title, url, icon, display_order, visit_count) VALUES "  # noqa: E501
            "(2, 1, '第二个项目', 'https://test.org', 'fas fa-globe', 1, 3)"
        )
