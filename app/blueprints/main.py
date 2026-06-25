import logging
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import Blueprint, jsonify, render_template, request
from werkzeug.utils import secure_filename

from app.config import config as app_config
from app.core.validators import (
    format_error_message,
    sanitize_filename,
    validate_form_data,
    validate_icon_path,
)
from app.services import db_service
from app.utils import generate_thumbnail, get_pinyin_data, get_version

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

CONFIG_IMG_PATH = app_config.images_path

_search_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
_SEARCH_CACHE_TTL = 60


def _get_cached_search(term: str) -> list[dict[str, Any]] | None:
    data = _search_cache.get(term)
    if data and time.time() - data[0] < _SEARCH_CACHE_TTL:
        return data[1]
    if data:
        del _search_cache[term]
    return None


def _set_cached_search(term: str, results: list[dict[str, Any]]) -> None:
    _search_cache[term] = (time.time(), results)


def clear_search_cache() -> None:
    _search_cache.clear()


def error_handler(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"文件未找到: {e}")
            return jsonify({"error": "配置文件未找到"}), 404
        except Exception as e:
            from werkzeug.exceptions import HTTPException
            if isinstance(e, HTTPException):
                return jsonify({"error": e.description}), e.code
            logger.error(f"未知错误: {e}")
            return jsonify({"error": "服务器内部错误"}), 500

    return decorated_function


@main_bp.route("/")
@error_handler
def index() -> str:
    categories = db_service.get_categories()
    categories_data = [
        {"name": category["name"], "nav_items": category["items"]}
        for category in categories
    ]

    frequent_items = db_service.get_frequent_items(20)

    icon_files: list[str] = []
    if os.path.exists(CONFIG_IMG_PATH):
        icon_files = sorted(
            [
                f
                for f in os.listdir(CONFIG_IMG_PATH)
                if os.path.isfile(os.path.join(CONFIG_IMG_PATH, f))
            ]
        )

    return render_template(
        "index.html",
        categories=categories_data,
        version=get_version(),
        frequent_items=frequent_items,
        icon_files=icon_files,
    )


@main_bp.route("/config", methods=["POST"])
@error_handler
def config() -> Any:
    return handle_config_post()


def handle_config_post() -> Any:
    clear_search_cache()
    action = request.form.get("action")

    if action == "add":
        return handle_add_item()
    elif action == "add_category":
        return handle_add_category()
    elif action == "edit_category":
        return handle_edit_category()
    elif action == "delete_category":
        return handle_delete_category()
    elif action == "edit":
        return handle_edit_item()
    elif action == "delete":
        return handle_delete_item()
    elif action == "reorder":
        return handle_reorder_items()
    elif action == "reorder_categories":
        return handle_reorder_categories()
    elif action in ["move_up", "move_down"]:
        return handle_move_item()
    else:
        return jsonify({"error": "未知操作"}), 400


def handle_add_category() -> Any:
    validation = validate_form_data(request.form, ["category"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    category_name = request.form.get("category", "")
    db_service.get_or_create_category(category_name.strip())

    return jsonify({"success": True, "message": "分类已添加"})


def handle_edit_category() -> Any:
    old_category = request.form.get("old_category")
    new_category = request.form.get("new_category")

    if not old_category or not old_category.strip():
        return jsonify({"error": "原分类名称不能为空"}), 400
    if not new_category or not new_category.strip():
        return jsonify({"error": "新分类名称不能为空"}), 400

    if old_category.strip() == new_category.strip():
        return jsonify({"success": True, "message": "分类名称未变更"})

    old_category_obj = db_service.get_category_by_name(old_category.strip())
    if not old_category_obj:
        return jsonify({"error": "原分类不存在"}), 400

    new_category_obj = db_service.get_category_by_name(new_category.strip())
    if new_category_obj:
        return jsonify({"error": "分类名称已存在"}), 400

    db_service.update_category_name(old_category.strip(), new_category.strip())

    return jsonify({"success": True, "message": "分类已更新"})


def handle_delete_category() -> Any:
    category_name = request.form.get("category")

    if not category_name or not category_name.strip():
        return jsonify({"error": "分类名称不能为空"}), 400

    category = db_service.get_category_by_name(category_name.strip())
    if not category:
        return jsonify({"error": "分类不存在"}), 400

    db_service.delete_category(category_name.strip())

    return jsonify({"success": True, "message": "分类已删除"})


def handle_add_item() -> Any:
    validation = validate_form_data(request.form, ["category", "title", "url"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    category = request.form.get("category", "")
    title = request.form.get("title", "")
    url = request.form.get("url", "")
    icon = request.files.get("icon")
    icon_path_param = request.form.get("icon_path")

    if icon_path_param:
        if not validate_icon_path(icon_path_param):
            return jsonify({"error": "无效的图标路径"}), 400
        icon_path: str = icon_path_param
    elif icon and icon.filename:
        _, ext = os.path.splitext(icon.filename)
        base = sanitize_filename(title) if title else ""
        if base:
            filename = base + ext if ext else base
        else:
            filename = sanitize_filename(secure_filename(icon.filename))
        if not filename:
            return jsonify({"error": "无效的文件名"}), 400
        save_path = os.path.join(CONFIG_IMG_PATH, filename)
        icon.save(save_path)
        generate_thumbnail(save_path, os.path.join(CONFIG_IMG_PATH, "thumbs"))
        icon_path = f"img/{filename}"
    else:
        icon_path = "fas fa-link"

    db_service.add_item(category, title, url, icon_path)

    return jsonify({"success": True, "message": "项目已添加", "icon_path": icon_path})


def handle_edit_item() -> Any:
    validation = validate_form_data(
        request.form,
        ["old_category", "old_title", "new_category", "new_title", "new_url"],
    )
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    old_category = request.form.get("old_category", "")
    new_category = request.form.get("new_category", "")
    old_title = request.form.get("old_title", "")
    new_title = request.form.get("new_title", "")
    new_url = request.form.get("new_url", "").strip()
    new_icon = request.files.get("new_icon")
    new_icon_path_param = request.form.get("new_icon_path")

    if old_category == db_service.FREQUENT_CATEGORY_NAME:
        return jsonify({"error": "常用项目不支持编辑，仅支持删除"}), 400

    icon_path: str | None = None
    if new_icon_path_param:
        if not validate_icon_path(new_icon_path_param):
            return jsonify({"error": "无效的图标路径"}), 400
        icon_path = new_icon_path_param
    elif new_icon and new_icon.filename:
        _, ext = os.path.splitext(new_icon.filename)
        base = sanitize_filename(new_title) if new_title else ""
        if base:
            filename = base + ext if ext else base
        else:
            filename = sanitize_filename(secure_filename(new_icon.filename))
        if filename:
            save_path = os.path.join(CONFIG_IMG_PATH, filename)
            new_icon.save(save_path)
            generate_thumbnail(save_path, os.path.join(CONFIG_IMG_PATH, "thumbs"))
            icon_path = f"img/{filename}"

    original_item = db_service.find_item_by_category_and_title(
        old_category, old_title
    ) if old_category and old_title else None
    final_icon = icon_path
    if not final_icon:
        final_icon = str(original_item.get("icon")) if original_item else "fas fa-link"

    if old_category == new_category:
        db_service.update_item(
            old_category,
            old_title,
            new_title,
            new_url,
            final_icon,
        )
    else:
        new_cat = db_service.get_category_by_name(new_category)
        if not new_cat:
            return jsonify({"error": "目标分类不存在"}), 400
        if not db_service.move_item_between_categories(old_category, new_category, old_title):
            return jsonify({"error": "移动项目失败"}), 400
        db_service.update_item(
            new_category,
            old_title,
            new_title,
            new_url,
            final_icon,
        )

    return jsonify(
        {
            "success": True,
            "message": "项目已更新",
            "icon_path": final_icon,
        }
    )


def handle_delete_item() -> Any:
    category_name = request.form.get("category", "")
    if not category_name:
        return jsonify({"error": "分类名称是必需的"}), 400

    if category_name == db_service.FREQUENT_CATEGORY_NAME:
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({"error": "常用项目删除需要提供 url"}), 400
        db_service.delete_item_by_url(url)
        return jsonify({"success": True, "message": "项目已删除"})

    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    title = request.form.get("title", "")

    db_service.delete_item(category_name, title)

    return jsonify({"success": True, "message": "项目已删除"})


def handle_reorder_items() -> Any:
    category_name = request.form.get("category", "").strip()
    if not category_name:
        return jsonify({"error": "分类名称是必需的"}), 400

    order = request.form.getlist("order[]") or request.form.get("order", "")

    if isinstance(order, str):
        order_list = [t.strip() for t in order.split(",") if t.strip()]
    elif isinstance(order, list):
        order_list = [t.strip() for t in order if t.strip()]
    else:
        order_list = []

    if not order_list:
        return jsonify({"error": "排序列表不能为空"}), 400

    if not db_service.reorder_items(category_name, order_list):
        return jsonify({"error": "分类不存在或排序失败"}), 400

    return jsonify({"success": True, "message": "项目顺序已更新"})


def handle_reorder_categories() -> Any:
    order = request.form.getlist("order[]") or request.form.get("order")

    if isinstance(order, str):
        order_list = [t.strip() for t in order.split(",") if t.strip()]
    elif isinstance(order, list):
        order_list = [t.strip() for t in order if t.strip()]
    else:
        order_list = []

    if not order_list:
        return jsonify({"error": "排序列表不能为空"}), 400

    db_service.reorder_categories(order_list)
    return jsonify({"success": True, "message": "分类顺序已更新"})


def handle_move_item() -> Any:
    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    category_name = request.form.get("category", "")
    item_title = request.form.get("title", "")
    action = request.form.get("action", "")

    direction = "up" if action == "move_up" else "down"
    db_service.move_item(category_name, item_title, direction)

    return jsonify({"success": True, "message": "项目顺序已更新"})


@main_bp.route("/search")
@error_handler
def search() -> Any:
    search_term = request.args.get("term", "").strip()
    if not search_term:
        return jsonify([])

    search_term_lower = search_term.lower()

    cached = _get_cached_search(search_term_lower)
    if cached is not None:
        return jsonify(cached)

    try:
        categories = db_service.get_categories()
        results: list[dict[str, Any]] = []

        for category in categories:
            for item in category.get("items", []):
                title = item.get("title", "")
                url = item.get("url", "")

                if search_term_lower in title.lower() or search_term_lower in url.lower():
                    results.append(item)
                    continue

                pinyin_data = get_pinyin_data(title)
                if search_term_lower in pinyin_data["full"]:
                    results.append(item)
                    continue
                if search_term_lower in pinyin_data["initials"]:
                    results.append(item)
                    continue

        results.sort(key=lambda x: x.get("visit_count", 0) or 0, reverse=True)

        _set_cached_search(search_term_lower, results)
        return jsonify(results)

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return jsonify([])


@main_bp.route("/api/visit-stats", methods=["GET"])
@error_handler
def get_visit_stats() -> Any:
    stats = db_service.get_visit_stats()
    return jsonify(stats)


@main_bp.route("/api/visit-stats/record", methods=["POST"])
@error_handler
def record_visit() -> Any:
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400

    url = data.get("url", "").strip()
    title = data.get("title", "").strip()
    icon = data.get("icon", "fas fa-link")

    if not url or not title:
        return jsonify({"error": "url和title是必需的"}), 400

    updated_stat = db_service.record_visit(url, title, icon)

    return jsonify({"success": True, "data": updated_stat})
