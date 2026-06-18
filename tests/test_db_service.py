"""
数据库服务单元测试
"""

from typing import Any

import pytest

from app.services.db_service import DbService


@pytest.fixture(autouse=True)
def clean_db(db: Any) -> None:
    """每个测试前清空数据"""
    with db.get_cursor() as cursor:
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM categories")


@pytest.fixture
def service(db: Any) -> DbService:
    """创建服务实例"""
    return DbService()


class TestCategories:
    def test_create_and_get(self, service: DbService) -> None:
        category = service.get_or_create_category("工作")
        assert category["name"] == "工作"
        assert category["id"] is not None

    def test_get_or_create_returns_existing(self, service: DbService) -> None:
        cat1 = service.get_or_create_category("工作")
        cat2 = service.get_or_create_category("工作")
        assert cat1["id"] == cat2["id"]

    def test_get_categories_empty(self, service: DbService) -> None:
        categories = service.get_categories()
        assert categories == []

    def test_get_categories_with_items(self, service: DbService) -> None:
        service.get_or_create_category("工作")
        service.add_item("工作", "Test", "https://example.com")
        categories = service.get_categories()
        assert len(categories) == 1
        assert len(categories[0]["items"]) == 1

    def test_get_category_by_name(self, service: DbService) -> None:
        service.get_or_create_category("工作")
        cat = service.get_category_by_name("工作")
        assert cat is not None
        assert cat["name"] == "工作"

    def test_get_category_by_name_not_found(self, service: DbService) -> None:
        cat = service.get_category_by_name("不存在")
        assert cat is None

    def test_update_category_name(self, service: DbService) -> None:
        service.get_or_create_category("工作")
        result = service.update_category_name("工作", "Work")
        assert result is True
        assert service.get_category_by_name("Work") is not None
        assert service.get_category_by_name("工作") is None

    def test_update_category_name_not_found(self, service: DbService) -> None:
        result = service.update_category_name("不存在", "NewName")
        assert result is False

    def test_delete_category(self, service: DbService) -> None:
        service.get_or_create_category("工作")
        service.add_item("工作", "Test", "https://example.com")
        result = service.delete_category("工作")
        assert result is True
        assert service.get_category_by_name("工作") is None
        categories = service.get_categories()
        assert len(categories) == 0

    def test_delete_category_not_found(self, service: DbService) -> None:
        result = service.delete_category("不存在")
        assert result is False

    def test_reorder_categories(self, service: DbService) -> None:
        service.get_or_create_category("A")
        service.get_or_create_category("B")
        result = service.reorder_categories(["B", "A"])
        assert result is True
        cats = service.get_categories(include_items=False)
        assert cats[0]["name"] == "B"
        assert cats[0]["display_order"] == 0
        assert cats[1]["name"] == "A"
        assert cats[1]["display_order"] == 1

    def test_reorder_categories_empty(self, service: DbService) -> None:
        assert service.reorder_categories([]) is False


class TestItems:
    def test_add_item(self, service: DbService) -> None:
        item = service.add_item("工作", "GitHub", "https://github.com")
        assert item["title"] == "GitHub"
        assert item["url"] == "https://github.com"
        assert item["visit_count"] == 0

    def test_add_item_auto_creates_category(self, service: DbService) -> None:
        service.add_item("新分类", "Test", "https://test.com")
        cat = service.get_category_by_name("新分类")
        assert cat is not None

    def test_find_item_by_url(self, service: DbService) -> None:
        service.add_item("工作", "GitHub", "https://github.com")
        item = service.find_item_by_url("https://github.com")
        assert item is not None
        assert item["title"] == "GitHub"

    def test_find_item_by_url_not_found(self, service: DbService) -> None:
        assert service.find_item_by_url("https://notfound.com") is None

    def test_find_item(self, service: DbService) -> None:
        cat = service.get_or_create_category("工作")
        service.add_item("工作", "GitHub", "https://github.com")
        item = service.find_item(cat["id"], "GitHub")
        assert item is not None
        assert item["url"] == "https://github.com"

    def test_update_item(self, service: DbService) -> None:
        service.add_item("工作", "GitHub", "https://github.com")
        result = service.update_item(  # noqa: E501
            "工作", "GitHub", "GitLab", "https://gitlab.com", "fab fa-gitlab"
        )
        assert result is True
        item = service.find_item_by_url("https://gitlab.com")
        assert item is not None
        assert item["title"] == "GitLab"

    def test_update_item_category_not_found(self, service: DbService) -> None:
        result = service.update_item("不存在", "Old", "New", "https://x.com", "icon")
        assert result is False

    def test_delete_item(self, service: DbService) -> None:
        service.add_item("工作", "GitHub", "https://github.com")
        result = service.delete_item("工作", "GitHub")
        assert result is True
        assert service.find_item_by_url("https://github.com") is None

    def test_delete_item_not_found(self, service: DbService) -> None:
        result = service.delete_item("工作", "不存在")
        assert result is False

    def test_reorder_items(self, service: DbService) -> None:
        service.add_item("工作", "A", "https://a.com")
        service.add_item("工作", "B", "https://b.com")
        service.reorder_items("工作", ["B", "A"])
        items = service.get_categories()[0]["items"]
        assert items[0]["title"] == "B"
        assert items[1]["title"] == "A"

    def test_move_item_up(self, service: DbService) -> None:
        service.get_or_create_category("工作")
        service.add_item("工作", "A", "https://a.com")
        service.add_item("工作", "B", "https://b.com")
        # 将 B 移到 A 上面
        service.move_item("工作", "B", "up")
        items = service.get_categories()[0]["items"]
        assert items[0]["title"] == "B"
        assert items[1]["title"] == "A"

    def test_move_item_down(self, service: DbService) -> None:
        service.add_item("工作", "A", "https://a.com")
        service.add_item("工作", "B", "https://b.com")
        service.move_item("工作", "A", "down")
        items = service.get_categories()[0]["items"]
        assert items[0]["title"] == "B"
        assert items[1]["title"] == "A"

    def test_move_item_at_boundary(self, service: DbService) -> None:
        """测试在边界移动不应报错"""
        service.add_item("工作", "A", "https://a.com")
        service.move_item("工作", "A", "up")
        items = service.get_categories()[0]["items"]
        assert len(items) == 1

    def test_move_item_between_categories(self, service: DbService) -> None:
        service.get_or_create_category("A")
        service.get_or_create_category("B")
        service.add_item("A", "Test", "https://test.com")
        result = service.move_item_between_categories("A", "B", "Test")
        assert result is True
        items_a = service.get_category_by_name("A")
        items_b = service.get_category_by_name("B")
        assert items_a is not None
        assert items_b is not None


class TestVisitStats:
    def test_record_visit_new_item(self, service: DbService) -> None:
        result = service.record_visit("https://example.com", "Example", "fas fa-link")
        assert result["visit_count"] == 0
        assert result["url"] == "https://example.com"

    def test_record_visit_existing_item(self, service: DbService) -> None:
        service.add_item("工作", "Example", "https://example.com")
        result = service.record_visit("https://example.com", "Example", "fas fa-link")
        assert result["visit_count"] == 1
        # 再次记录
        result2 = service.record_visit("https://example.com", "Example", "fas fa-link")
        assert result2["visit_count"] == 2

    def test_get_frequent_items(self, service: DbService) -> None:
        service.add_item("工作", "Popular", "https://popular.com")
        service.record_visit("https://popular.com", "Popular", "fas fa-star")
        service.record_visit("https://popular.com", "Popular", "fas fa-star")
        frequent = service.get_frequent_items(10)
        assert len(frequent) >= 1
        assert frequent[0]["visit_count"] >= 2

    def test_get_visit_stats(self, service: DbService) -> None:
        service.add_item("工作", "Test", "https://test.com")
        service.record_visit("https://test.com", "Test", "fas fa-link")
        service.record_visit("https://test.com", "Test", "fas fa-link")
        stats = service.get_visit_stats()
        assert "https://test.com" in stats
        assert stats["https://test.com"]["visit_count"] >= 2

    def test_delete_item_by_url(self, service: DbService) -> None:
        service.add_item("工作", "Test", "https://test.com")
        result = service.delete_item_by_url("https://test.com")
        assert result is True
        assert service.find_item_by_url("https://test.com") is None

    def test_delete_item_by_url_not_found(self, service: DbService) -> None:
        result = service.delete_item_by_url("https://notfound.com")
        assert result is False
