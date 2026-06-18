#!/usr/bin/env python3
"""
数据迁移脚本：从 JSON 文件迁移到 SQLite 数据库

使用方法:
    python migrate.py

迁移内容:
    - config.json 中的分类和项目
    - visit_stats.json 中的访问统计数据
"""

import json
import sqlite3
import sys
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    return current_file.parent


def migrate(config_path: str, db_path: str, stats_path: str | None = None) -> bool:
    """执行数据迁移"""

    config_file = Path(config_path)
    if not config_file.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        return False

    with open(config_file, encoding="utf-8") as f:
        config_data = json.load(f)

    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

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
        CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_visit_count ON items(visit_count DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_url ON items(url)
    """)

    categories = config_data.get("categories", [])
    print(f"找到 {len(categories)} 个分类")

    category_map = {}
    for i, category in enumerate(categories):
        cat_name = category.get("name", "")
        cat_icon = category.get("icon")

        cursor.execute(
            "INSERT INTO categories (name, icon, display_order) VALUES (?, ?, ?)",
            (cat_name, cat_icon, i),
        )
        category_id = cursor.lastrowid
        category_map[cat_name] = category_id

        items = category.get("items", [])
        for j, item in enumerate(items):
            title = item.get("title", "")
            url = item.get("url", "")
            icon = item.get("icon", "fas fa-link")

            sql = "INSERT INTO items (category_id, title, url, icon, display_order, visit_count, last_visit) VALUES (?, ?, ?, ?, ?, 0, NULL)"  # noqa: E501
            cursor.execute(sql,
                (category_id, title, url, icon, j),
            )

        print(f"  - {cat_name}: {len(items)} 个项目")

    if stats_path:
        stats_file = Path(stats_path)
        if stats_file.exists():
            with open(stats_file, encoding="utf-8") as f:
                stats_data = json.load(f)

            print("迁移访问统计数据...")

            for url, stat in stats_data.items():
                title = stat.get("title", "")
                icon = stat.get("icon", "fas fa-link")
                count = stat.get("count", 0)
                last_visit = stat.get("lastVisit")

                cursor.execute(
                    """UPDATE items SET visit_count = ?, last_visit = ?
                       WHERE url = ?""",
                    (count, last_visit, url),
                )

            print(f"  - 已更新 {len(stats_data)} 条访问记录")
        else:
            print(f"警告: 访问统计文件不存在: {stats_path}")

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]

    print("\n迁移完成!")
    print(f"  - 分类: {cat_count}")
    print(f"  - 项目: {item_count}")
    print(f"  - 数据库: {db_path}")

    conn.close()
    return True


def main() -> None:
    project_root = get_project_root()

    config_path = project_root / "config" / "config.json"
    db_path = project_root / "config" / "homer.db"
    stats_path = project_root / "config" / "visit_stats.json"

    print("=" * 50)
    print("Homer 数据迁移工具")
    print("=" * 50)
    print(f"源配置文件: {config_path}")
    print(f"目标数据库: {db_path}")
    print(f"访问统计:  {stats_path}")
    print("-" * 50)

    if not config_path.exists():
        print("错误: 配置文件不存在!")
        print(f"\n请确保 {config_path} 存在，或手动创建空配置:")
        print("  echo '{\"categories\": []}' > config/config.json")
        sys.exit(1)

    try:
        success = migrate(str(config_path), str(db_path), str(stats_path))
        if success:
            print("\n迁移成功! 现在可以启动应用了。")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n迁移失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
