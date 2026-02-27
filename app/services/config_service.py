from pathlib import Path
from typing import Dict, Any, Optional, List

from app.core.base_manager import BaseManager
from app.config import config as app_config


class ConfigService(BaseManager):
    """配置服务 - 管理分类和项目数据"""

    def __init__(self):
        super().__init__(Path(app_config.config_path), app_config.cache_ttl)
        if not app_config.validate_config():
            raise RuntimeError("Configuration validation failed")

    def _get_default_data(self) -> Dict[str, Any]:
        return {"categories": []}

    def get_categories(self) -> List[Dict[str, Any]]:
        config = self.load()
        return config.get("categories", [])

    def find_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        categories = self.get_categories()
        for cat in categories:
            if cat.get("name") == name:
                return cat
        return None

    def find_item_in_category(
        self, category_name: str, item_title: str
    ) -> Optional[Dict[str, Any]]:
        category = self.find_category_by_name(category_name)
        if not category:
            return None
        items = category.get("items", [])
        for item in items:
            if item.get("title") == item_title:
                return item
        return None

    def add_item_to_category(self, category_name: str, item: Dict[str, Any]) -> None:
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    if "items" not in category:
                        category["items"] = []
                    category["items"].append(item)
                    break
            return config

        self.update(updater)

    def update_item_in_category(
        self, category_name: str, old_title: str, new_item: Dict[str, Any]
    ) -> None:
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    for i, item in enumerate(items):
                        if item.get("title") == old_title:
                            items[i] = new_item
                            break
                    break
            return config

        self.update(updater)

    def remove_item_from_category(self, category_name: str, item_title: str) -> None:
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    category["items"] = [
                        item for item in items if item.get("title") != item_title
                    ]
                    break
            return config

        self.update(updater)

    def reorder_items_in_category(self, category_name: str, order: List[str]) -> None:
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    items_map = {item.get("title"): item for item in items}
                    new_items = []
                    for title in order:
                        if title in items_map:
                            new_items.append(items_map.pop(title))
                    for item in items:
                        if item.get("title") in items_map:
                            new_items.append(item)
                    category["items"] = new_items
                    break
            return config

        self.update(updater)

    def move_item_in_category(
        self, category_name: str, item_title: str, direction: str
    ) -> None:
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    for i, item in enumerate(items):
                        if item.get("title") == item_title:
                            if direction == "up" and i > 0:
                                items[i], items[i - 1] = items[i - 1], items[i]
                            elif direction == "down" and i < len(items) - 1:
                                items[i], items[i + 1] = items[i + 1], items[i]
                            break
                    break
            return config

        self.update(updater)

    def move_item_between_categories(
        self, old_category: str, new_category: str, item_title: str
    ) -> None:
        def updater(config):
            item_to_move = None
            for category in config.get("categories", []):
                if category.get("name") == old_category:
                    items = category.get("items", [])
                    for i, item in enumerate(items):
                        if item.get("title") == item_title:
                            item_to_move = items.pop(i)
                            break
                    break
            if item_to_move:
                for category in config.get("categories", []):
                    if category.get("name") == new_category:
                        if "items" not in category:
                            category["items"] = []
                        category["items"].append(item_to_move)
                        break
            return config

        self.update(updater)


config_service = ConfigService()
