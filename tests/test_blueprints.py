"""
蓝图路由集成测试（使用 Flask 测试客户端）
"""
import json
from typing import Any

import pytest
from flask.testing import FlaskClient

from app.services.db_service import DbService


class TestIndexRoute:
    def test_index_contains_svg_icon(self, client: FlaskClient, sample_data: Any) -> None:
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'class="nav-item-icon"' in html
        assert 'class="icon-svg"' in html

    def test_index_contains_img_icon_when_icon_path_is_img(
        self, client: FlaskClient, db: Any
    ) -> None:
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM categories")
        svc = DbService()
        svc.get_or_create_category("测试")
        svc.add_item("测试", "自定义图", "https://example.com", "img/custom.png")
        resp = client.get("/")
        html = resp.data.decode()
        assert 'src="/config/img/thumbs/custom.png"' in html
        assert 'class="icon-img"' in html

    def test_thumbnail_generated_on_the_fly(
        self, client: FlaskClient, db: Any, tmp_path: Any, monkeypatch: Any
    ) -> None:
        from PIL import Image

        from app.config import config as app_config
        img_dir = tmp_path / "img"
        img_dir.mkdir(parents=True)
        monkeypatch.setattr(app_config, "images_dir", img_dir)
        src = str(img_dir / "test.png")
        Image.new("RGB", (200, 300), color="blue").save(src)
        resp = client.get("/config/img/thumbs/test.png")
        assert resp.status_code == 200
        assert (img_dir / "thumbs" / "test.png").exists()

    def test_thumbnail_fallback_to_original_for_svg(
        self, client: FlaskClient, db: Any, tmp_path: Any, monkeypatch: Any
    ) -> None:
        from app.config import config as app_config
        img_dir = tmp_path / "img"
        img_dir.mkdir(parents=True)
        monkeypatch.setattr(app_config, "images_dir", img_dir)
        svg_path = img_dir / "icon.svg"
        svg_path.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
        resp = client.get("/config/img/thumbs/icon.svg")
        assert resp.status_code == 200
        assert not (img_dir / "thumbs" / "icon.svg").exists()

    def test_index_icons_in_frequent_section(
        self, client: FlaskClient, sample_data: Any
    ) -> None:
        resp = client.get("/")
        html = resp.data.decode()
        assert 'class="icon-svg"' in html
        assert 'class="icon-img"' not in html

    def test_index_contains_click_badge_in_regular_categories(
        self, client: FlaskClient, sample_data: Any
    ) -> None:
        resp = client.get("/")
        html = resp.data.decode()
        assert 'class="click-badge"' in html
        assert ">5<" in html
        assert ">3<" in html

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

    def test_add_item_invalid_icon_path(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={
            "action": "add",
            "category": "测试分类",
            "title": "项目",
            "url": "https://example.com",
            "icon_path": "../../etc/passwd",
        })
        assert resp.status_code == 400
        assert "无效的图标路径" in resp.get_json()["error"]

    def test_edit_item_to_nonexistent_category(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "来源分类"})
        client.post("/config", data={
            "action": "add",
            "category": "来源分类",
            "title": "项目",
            "url": "https://example.com",
        })
        resp = client.post("/config", data={
            "action": "edit",
            "old_category": "来源分类",
            "new_category": "不存在的分类",
            "old_title": "项目",
            "new_title": "新标题",
            "new_url": "https://new.com",
            "old_url": "https://example.com",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "目标分类不存在"

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

    def test_reorder_items_persists_order(self, client: FlaskClient, db: Any) -> None:
        client.post("/config", data={"action": "add_category", "category": "分类"})
        client.post("/config", data={
            "action": "add", "category": "分类", "title": "A", "url": "https://a.com",
        })
        client.post("/config", data={
            "action": "add", "category": "分类", "title": "B", "url": "https://b.com",
        })
        resp = client.post("/config", data={
            "action": "reorder", "category": "分类", "order": "B,A",
        })
        assert resp.status_code == 200

        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT title, display_order FROM items"
                " WHERE category_id = (SELECT id FROM categories WHERE name = ?)"
                " ORDER BY display_order",
                ("分类",),
            )
            rows = cursor.fetchall()
            assert len(rows) == 2
            assert rows[0]["title"] == "B"
            assert rows[1]["title"] == "A"

    def test_reorder_items_whitespace_category(self, client: FlaskClient) -> None:
        client.post("/config", data={"action": "add_category", "category": "分类"})
        client.post("/config", data={
            "action": "add", "category": "分类", "title": "A", "url": "https://a.com",
        })
        resp = client.post("/config", data={
            "action": "reorder", "category": "  分类  ", "order": "A",
        })
        assert resp.status_code == 200

    def test_reorder_items_nonexistent_category(self, client: FlaskClient) -> None:
        resp = client.post("/config", data={
            "action": "reorder", "category": "不存在的分类", "order": "A",
        })
        assert resp.status_code == 400


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

    def test_search_pinyin_full(self, client: FlaskClient) -> None:
        svc = DbService()
        svc.get_or_create_category("工具")
        svc.add_item("工具", "百度", "https://baidu.com")

        resp = client.get("/search?term=baidu")
        assert resp.status_code == 200
        data = resp.get_json()
        titles = [item["title"] for item in data]
        assert "百度" in titles

    def test_search_pinyin_initials(self, client: FlaskClient) -> None:
        svc = DbService()
        svc.get_or_create_category("社交")
        svc.add_item("社交", "微信", "https://weixin.qq.com")

        resp = client.get("/search?term=wx")
        assert resp.status_code == 200
        data = resp.get_json()
        titles = [item["title"] for item in data]
        assert "微信" in titles

    def test_search_pinyin_initials_partial(self, client: FlaskClient) -> None:
        svc = DbService()
        svc.get_or_create_category("云服务")
        svc.add_item("云服务", "百度云", "https://pan.baidu.com")

        resp = client.get("/search?term=bdy")
        assert resp.status_code == 200
        data = resp.get_json()
        titles = [item["title"] for item in data]
        assert "百度云" in titles

    def test_search_sorted_by_visit_count(self, client: FlaskClient) -> None:
        svc = DbService()
        svc.get_or_create_category("常用")
        svc.add_item("常用", "Site A", "https://a.com")
        svc.add_item("常用", "Site B", "https://b.com")

        svc.record_visit("https://b.com", "Site B", "fas fa-link")
        svc.record_visit("https://b.com", "Site B", "fas fa-link")
        svc.record_visit("https://a.com", "Site A", "fas fa-link")

        resp = client.get("/search?term=site")
        assert resp.status_code == 200
        data = resp.get_json()
        titles = [item["title"] for item in data]
        assert titles == ["Site B", "Site A"]

    def test_search_cache_hit(self, client: FlaskClient) -> None:
        resp_first = client.get("/search?term=git")
        assert resp_first.status_code == 200
        data_first = resp_first.get_json()

        resp_second = client.get("/search?term=git")
        assert resp_second.status_code == 200
        data_second = resp_second.get_json()

        assert data_first == data_second

    def test_search_title_no_html_tags(self, client: FlaskClient) -> None:
        svc = DbService()
        svc.get_or_create_category("测试")
        svc.add_item("测试", "MangaTag", "https://example.com/manga")

        resp = client.get("/search?term=Tag")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 1
        for item in data:
            assert "<mark>" not in item.get("title", "")
            assert "</mark>" not in item.get("title", "")


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
