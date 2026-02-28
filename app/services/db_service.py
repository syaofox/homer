import time
import logging
from typing import Dict, Any, Optional, List

from app.database import get_db

logger = logging.getLogger(__name__)


class DbService:
    """数据库服务 - 管理分类、项目和访问统计"""

    FREQUENT_CATEGORY_NAME = "常用"
    FREQUENT_ITEMS_LIMIT = 20

    def __init__(self):
        self.db = get_db()

    def get_categories(self, include_items: bool = True) -> List[Dict[str, Any]]:
        """获取所有分类"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, name, icon, display_order FROM categories ORDER BY display_order, id"
            )
            categories = [dict(row) for row in cursor.fetchall()]

            if include_items:
                for category in categories:
                    category["items"] = self._get_items_by_category(
                        cursor, category["id"]
                    )

            return categories

    def _get_items_by_category(self, cursor, category_id: int) -> List[Dict[str, Any]]:
        """获取指定分类的所有项目"""
        cursor.execute(
            """SELECT id, category_id, title, url, icon, display_order, 
                      visit_count, last_visit 
               FROM items 
               WHERE category_id = ? 
               ORDER BY display_order, id""",
            (category_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找分类"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, name, icon, display_order FROM categories WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_or_create_category(
        self, name: str, icon: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取或创建分类"""
        category = self.get_category_by_name(name)
        if category:
            return category

        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO categories (name, icon) VALUES (?, ?)",
                (name, icon),
            )
            return {
                "id": cursor.lastrowid,
                "name": name,
                "icon": icon,
                "display_order": 0,
            }

    def find_item(self, category_id: int, title: str) -> Optional[Dict[str, Any]]:
        """在分类中查找项目"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT id, category_id, title, url, icon, display_order,
                          visit_count, last_visit 
                   FROM items 
                   WHERE category_id = ? AND title = ?""",
                (category_id, title),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def find_item_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """根据 URL 查找项目"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT id, category_id, title, url, icon, display_order,
                          visit_count, last_visit 
                   FROM items 
                   WHERE url = ?""",
                (url,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_item(
        self, category_name: str, title: str, url: str, icon: str = "fas fa-link"
    ) -> Dict[str, Any]:
        """添加项目到分类"""
        category = self.get_or_create_category(category_name)

        with self.db.get_cursor() as cursor:
            cursor.execute(
                """INSERT INTO items (category_id, title, url, icon, visit_count, last_visit)
                   VALUES (?, ?, ?, ?, 0, NULL)""",
                (category["id"], title, url, icon),
            )

            return {
                "id": cursor.lastrowid,
                "category_id": category["id"],
                "title": title,
                "url": url,
                "icon": icon,
                "visit_count": 0,
                "last_visit": None,
            }

    def update_item(
        self,
        category_name: str,
        old_title: str,
        new_title: str,
        new_url: str,
        new_icon: str,
    ) -> bool:
        """更新项目"""
        category = self.get_category_by_name(category_name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute(
                """UPDATE items 
                   SET title = ?, url = ?, icon = ?
                   WHERE category_id = ? AND title = ?""",
                (new_title, new_url, new_icon, category["id"], old_title),
            )
            return cursor.rowcount > 0

    def delete_item(self, category_name: str, title: str) -> bool:
        """删除项目"""
        category = self.get_category_by_name(category_name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM items WHERE category_id = ? AND title = ?",
                (category["id"], title),
            )
            return cursor.rowcount > 0

    def move_item(self, category_name: str, item_title: str, direction: str) -> bool:
        """移动项目上下位置"""
        category = self.get_category_by_name(category_name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT id, display_order FROM items 
                   WHERE category_id = ? AND title = ?""",
                (category["id"], item_title),
            )
            item = cursor.fetchone()
            if not item:
                return False

            current_order = item["display_order"]
            if direction == "up":
                new_order = current_order - 1
            else:
                new_order = current_order + 1

            cursor.execute(
                "UPDATE items SET display_order = ? WHERE id = ?",
                (new_order, item["id"]),
            )
            return True

    def reorder_items(self, category_name: str, order: List[str]) -> bool:
        """重新排序项目"""
        category = self.get_category_by_name(category_name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            for i, title in enumerate(order):
                cursor.execute(
                    "UPDATE items SET display_order = ? WHERE category_id = ? AND title = ?",
                    (i, category["id"], title),
                )
            return True

    def move_item_between_categories(
        self,
        old_category: str,
        new_category: str,
        item_title: str,
    ) -> bool:
        """移动项目到另一个分类"""
        old_cat = self.get_category_by_name(old_category)
        new_cat = self.get_category_by_name(new_category)

        if not old_cat or not new_cat:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute(
                "UPDATE items SET category_id = ? WHERE category_id = ? AND title = ?",
                (new_cat["id"], old_cat["id"], item_title),
            )
            return cursor.rowcount > 0

    def record_visit(self, url: str, title: str, icon: str) -> Dict[str, Any]:
        """记录访问次数"""
        current_time = int(time.time() * 1000)

        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT id, category_id, title, url, icon, display_order,
                          visit_count, last_visit 
                   FROM items WHERE url = ?""",
                (url,),
            )
            item = cursor.fetchone()

            if item:
                cursor.execute(
                    """UPDATE items 
                       SET visit_count = visit_count + 1, last_visit = ?, title = ?, icon = ?
                       WHERE url = ?""",
                    (current_time, title, icon, url),
                )
                return {
                    "id": item["id"],
                    "category_id": item["category_id"],
                    "title": title,
                    "url": url,
                    "icon": icon,
                    "visit_count": item["visit_count"] + 1,
                    "last_visit": current_time,
                }
            else:
                return {
                    "id": None,
                    "title": title,
                    "url": url,
                    "icon": icon,
                    "visit_count": 0,
                    "last_visit": None,
                }

    def get_frequent_items(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最常访问的项目"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT id, category_id, title, url, icon, display_order,
                          visit_count, last_visit 
                   FROM items 
                   WHERE visit_count > 0 
                   ORDER BY visit_count DESC, last_visit DESC 
                   LIMIT ?""",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def sync_frequent_category(self) -> None:
        """同步常用分类：根据访问次数自动更新常用分类"""
        frequent = self.get_frequent_items(self.FREQUENT_ITEMS_LIMIT)

        frequent_cat = self.get_or_create_category(self.FREQUENT_CATEGORY_NAME)

        with self.db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM items WHERE category_id = ?",
                (frequent_cat["id"],),
            )

            for item in frequent:
                cursor.execute(
                    """INSERT INTO items (category_id, title, url, icon, visit_count, last_visit)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        frequent_cat["id"],
                        item["title"],
                        item["url"],
                        item["icon"],
                        item["visit_count"],
                        item["last_visit"],
                    ),
                )

    def get_visit_stats(self) -> Dict[str, Any]:
        """获取访问统计"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT title, url, icon, visit_count, last_visit 
                   FROM items 
                   WHERE visit_count > 0 
                   ORDER BY visit_count DESC"""
            )
            stats = {}
            for row in cursor.fetchall():
                stats[row["url"]] = dict(row)
            return stats

    def remove_stat_by_url(self, url: str) -> bool:
        """删除指定 URL 的访问统计"""
        with self.db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE url = ?", (url,))
            return cursor.rowcount > 0


db_service = DbService()
