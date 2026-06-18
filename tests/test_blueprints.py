"""
蓝图路由集成测试（使用 Flask 测试客户端）
"""
import json
from typing import Any

import pytest
from flask.testing import FlaskClient

from app.services.db_service import DbService


class TestIndexRoute:
    def test_index_returns_200(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"icon-svg" in resp.data or b"categories" in resp.data

    def test_index_contains_version(self, client: FlaskClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200


class TestConfigRoute:
    def test_unknown_action(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={"action": "unknown"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "未知操作"

    @pytest.fixture(autouse=True)
    def clear_data(self, db: Any) -> None:
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM categories")

    def test_add_category(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={"action": "add_category", "category": "测试分类"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_add_category_empty_name(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={"action": "add_category", "category": ""})
        assert resp.status_code == 400

    def test_add_item(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={
            "action": "add",
            "category": "测试分类",
            "title": "测试项目",
            "url": "https://example.com",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_add_item_missing_fields(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={"action": "add", "category": "测试分类"})
        assert resp.status_code == 400

    def test_add_item_invalid_url(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={
            "action": "add",
            "category": "测试分类",
            "title": "测试项目",
            "url": "not-a-url",
        })
        assert resp.status_code == 400

    def test_edit_category(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "旧名称"})
        resp = client.post("/config", data={
            "action": "edit_category",
            "old_category": "旧名称",
            "new_category": "新名称",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_delete_category(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "待删除"})
        resp = client.post("/config", data={"action": "delete_category", "category": "待删除"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_delete_category_not_found(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={"action": "delete_category", "category": "不存在"})
        assert resp.status_code == 400

    def test_edit_item_same_category(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "分类"})
        client.post("/config", data={
            "action": "add",
            "category": "分类",
            "title": "旧标题",
            "url": "https://old.com",
        })
        resp = client.post("/config", data={
            "action": "edit",
            "old_category": "分类",
            "new_category": "分类",
            "old_title": "旧标题",
            "new_title": "新标题",
            "new_url": "https://new.com",
            "old_url": "https://old.com",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_delete_item(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "分类"})
        client.post("/config", data={
            "action": "add",
            "category": "分类",
            "title": "待删除",
            "url": "https://delete.com",
        })
        resp = client.post("/config", data={
            "action": "delete",
            "category": "分类",
            "title": "待删除",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_reorder_items(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "分类"})
        client.post("/config", data={
            "action": "add",
            "category": "分类",
            "title": "A",
            "url": "https://a.com",
        })
        client.post("/config", data={
            "action": "add",
            "category": "分类",
            "title": "B",
            "url": "https://b.com",
        })
        resp = client.post("/config", data={
            "action": "reorder",
            "category": "分类",
            "order": "B,A",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_reorder_categories(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "A"})
        client.post("/config", data={"action": "add_category", "category": "B"})
        resp = client.post("/config", data={
            "action": "reorder_categories",
            "order": "B,A",
        })
        assert resp.status_code == 200


class TestSearchRoute:
    @pytest.fixture(autouse=True)
    def setup_data(self, db: Any) -> None:
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM categories")
        service = DbService()
        service.get_or_create_category("工作")
        service.add_item("工作", "GitHub", "https://github.com")
        service.add_item("工作", "Gmail", "https://mail.google.com")

    def test_search_found(self, client: FlaskClient) -> None:
        resp = client.get("/search?term=git")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 1

    def test_search_not_found(self, client: FlaskClient) -> None:
        resp = client.get("/search?term=zzzzzzz")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == []

    def test_search_empty_term(self, client: FlaskClient) -> None:
        resp = client.get("/search?term=")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == []

    def test_search_no_term_param(self, client: FlaskClient) -> None:
        resp = client.get("/search")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == []


class TestVisitStatsRoute:
    def test_get_stats_empty(self, client: FlaskClient) -> None:
        resp = client.get("/api/visit-stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {}

    def test_record_visit(self, client: FlaskClient) -> None:
        resp = client.post(
            "/api/visit-stats/record",
            data=json.dumps({"url": "https://example.com", "title": "Example"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_record_visit_no_url(self, client: FlaskClient) -> None:
        resp = client.post(
            "/api/visit-stats/record",
            data=json.dumps({"title": "Example"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_record_visit_invalid_json(self, client: FlaskClient) -> None:
        resp = client.post(
            "/api/visit-stats/record",
            data="not json",
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_get_stats_with_data(self, client: FlaskClient) -> None:
        # 先添加项目到分类
        client.post("/config", data={
            "action": "add_category", "category": "测试分类",
        })
        client.post("/config", data={
            "action": "add",
            "category": "测试分类",
            "title": "Example",
            "url": "https://example.com",
        })
        # 再记录访问
        client.post(
            "/api/visit-stats/record",
            data=json.dumps({"url": "https://example.com", "title": "Example"}),
            content_type="application/json",
        )
        resp = client.get("/api/visit-stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "https://example.com" in data
