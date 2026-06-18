import logging
import time
from typing import TYPE_CHECKING, Any

from app.database import get_db

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class DbService:
    """数据库服务 - 管理分类、项目和访问统计"""

    FREQUENT_CATEGORY_NAME = "常用"
    FREQUENT_ITEMS_LIMIT = 20

    @property
    def db(self) -> Any:
        """懒加载数据库实例，确保每次使用都获取最新单例"""
        return get_db()

    def get_categories(self, include_items: bool = True) -> list[dict[str, Any]]:
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

    def _get_items_by_category(self, cursor: Any, category_id: int) -> list[dict[str, Any]]:
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

    def get_category_by_name(self, name: str) -> dict[str, Any] | None:
        """根据名称查找分类"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT id, name, icon, display_order FROM categories WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_or_create_category(
        self, name: str, icon: str | None = None
    ) -> dict[str, Any]:
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

    def update_category_name(self, old_name: str, new_name: str) -> bool:
        """更新分类名称"""
        category = self.get_category_by_name(old_name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (new_name, category["id"]),
            )
            return bool(cursor.rowcount > 0)

    def delete_category(self, name: str) -> bool:
        """删除分类（同时删除该分类下的所有项目）"""
        category = self.get_category_by_name(name)
        if not category:
            return False

        with self.db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE category_id = ?", (category["id"],))
            cursor.execute("DELETE FROM categories WHERE id = ?", (category["id"],))
            return True

    def reorder_categories(self, order: list[str]) -> bool:
        """重新排序分类"""
        if not order:
            return False

        with self.db.get_cursor() as cursor:
            for i, name in enumerate(order):
                cursor.execute(
                    "UPDATE categories SET display_order = ? WHERE name = ?",
                    (i, name),
                )
            return True

    def find_item(self, category_id: int, title: str) -> dict[str, Any] | None:
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

    def find_item_by_url(self, url: str) -> dict[str, Any] | None:
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
    ) -> dict[str, Any]:
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
            return bool(cursor.rowcount > 0)

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
            return bool(cursor.rowcount > 0)

    def move_item(self, category_name: str, item_title: str, direction: str) -> bool:
        """移动项目上下位置（与相邻项目交换 display_order）"""
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
                target_order = current_order - 1
                # 找到上一个 display_order 的相邻项目
                cursor.execute(
                    """SELECT id, display_order FROM items
                       WHERE category_id = ? AND display_order < ?
                       ORDER BY display_order DESC LIMIT 1""",
                    (category["id"], current_order),
                )
            else:
                target_order = current_order + 1
                cursor.execute(
                    """SELECT id, display_order FROM items
                       WHERE category_id = ? AND display_order > ?
                       ORDER BY display_order ASC LIMIT 1""",
                    (category["id"], current_order),
                )

            neighbor = cursor.fetchone()
            if neighbor:
                # 交换 display_order
                cursor.execute(
                    "UPDATE items SET display_order = ? WHERE id = ?",
                    (neighbor["display_order"], item["id"]),
                )
                cursor.execute(
                    "UPDATE items SET display_order = ? WHERE id = ?",
                    (current_order, neighbor["id"]),
                )
            else:
                # 没有相邻项目（已经在边界），直接设置
                cursor.execute(
                    "UPDATE items SET display_order = ? WHERE id = ?",
                    (target_order, item["id"]),
                )
            return True

    def reorder_items(self, category_name: str, order: list[str]) -> bool:
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
            return bool(cursor.rowcount > 0)

    def record_visit(self, url: str, title: str, icon: str) -> dict[str, Any]:
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

    def get_frequent_items(self, limit: int = 20) -> list[dict[str, Any]]:
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
        """同步常用分类：现在只从 items 表按访问次数查询，不再在数据库中创建常用分类"""

    def get_visit_stats(self) -> dict[str, Any]:
        """获取访问统计"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """SELECT title, url, icon, visit_count, last_visit
                   FROM items
                   WHERE visit_count > 0
                   ORDER BY visit_count DESC"""
            )
            stats: dict[str, Any] = {}
            for row in cursor.fetchall():
                stats[row["url"]] = dict(row)
            return stats

    def remove_stat_by_url(self, url: str) -> bool:
        """删除指定 URL 的项目（清理统计和项目本身）"""
        with self.db.get_cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE url = ?", (url,))
            return bool(cursor.rowcount > 0)


db_service = DbService()
