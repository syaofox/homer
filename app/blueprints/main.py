import os
import logging
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, send_from_directory
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename

from app.config import config as app_config
from app.services import config_service, stats_service
from app.core.validators import (
    validate_form_data,
    validate_title,
    validate_url,
    validate_category_name,
    sanitize_filename,
    format_error_message,
)
from app.utils import icon_to_svg, is_fa_icon, get_version

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

CONFIG_IMG_PATH = app_config.images_path


def error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"文件未找到: {e}")
            return jsonify({"error": "配置文件未找到"}), 404
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return jsonify({"error": "服务器内部错误"}), 500

    return decorated_function


@main_bp.route("/")
@error_handler
def index():
    categories = config_service.get_categories()
    categories_data = [
        {"name": category["name"], "nav_items": category["items"]}
        for category in categories
    ]

    visit_stats = stats_service.get_visit_stats()
    top_sites = sorted(
        visit_stats.values(), key=lambda x: x.get("count", 0), reverse=True
    )[:20]
    frequent_items = [s for s in top_sites if s.get("count", 0) > 0]

    return render_template(
        "index.html",
        categories=categories_data,
        version=get_version(),
        frequent_items=frequent_items,
    )


@main_bp.route("/config", methods=["POST"])
@error_handler
def config():
    return handle_config_post()


def handle_config_post():
    action = request.form.get("action")

    if action == "add":
        return handle_add_item()
    elif action == "edit":
        return handle_edit_item()
    elif action == "delete":
        return handle_delete_item()
    elif action == "reorder":
        return handle_reorder_items()
    elif action in ["move_up", "move_down"]:
        return handle_move_item()
    else:
        return jsonify({"error": "未知操作"}), 400


def handle_add_item():
    validation = validate_form_data(request.form, ["category", "title", "url"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    category = request.form.get("category")
    title = request.form.get("title")
    url = request.form.get("url")
    icon = request.files.get("icon")

    if icon and icon.filename:
        filename = sanitize_filename(secure_filename(icon.filename))
        if not filename:
            return jsonify({"error": "无效的文件名"}), 400
        icon.save(os.path.join(CONFIG_IMG_PATH, filename))
        icon_path = f"img/{filename}"
    else:
        icon_path = "fas fa-link"

    new_item = {"title": title, "icon": icon_path, "url": url}
    config_service.add_item_to_category(category, new_item)

    return jsonify({"success": True, "message": "项目已添加"})


def handle_edit_item():
    validation = validate_form_data(
        request.form,
        ["old_category", "old_title", "new_category", "new_title", "new_url"],
    )
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    old_category = request.form.get("old_category")
    new_category = request.form.get("new_category")
    old_title = request.form.get("old_title")
    new_title = request.form.get("new_title")
    new_url = request.form.get("new_url").strip()
    new_icon = request.files.get("new_icon")
    old_url = request.form.get("old_url", "").strip()

    if old_category == "常用":
        return jsonify({"error": "常用项目不支持编辑，仅支持删除"}), 400

    icon_path = None
    if new_icon and new_icon.filename:
        filename = sanitize_filename(secure_filename(new_icon.filename))
        if filename:
            new_icon.save(os.path.join(CONFIG_IMG_PATH, filename))
            icon_path = f"img/{filename}"

    original_item = config_service.find_item_in_category(old_category, old_title)
    if not original_item:
        return jsonify({"error": "项目未找到"}), 404

    updated_item = {
        "title": new_title,
        "url": new_url,
        "icon": icon_path if icon_path else original_item["icon"],
    }

    if old_category == new_category:
        config_service.update_item_in_category(old_category, old_title, updated_item)
    else:
        config_service.remove_item_from_category(old_category, old_title)
        config_service.add_item_to_category(new_category, updated_item)

    old_item_url = (original_item.get("url") or "").strip()
    if old_item_url:
        stats = stats_service.get_visit_stats()
        if old_item_url in stats:
            stats_service.update_stat(
                old_item_url,
                new_url,
                new_title,
                updated_item["icon"],
            )

    return jsonify({"success": True, "message": "项目已更新"})


def handle_delete_item():
    category_name = request.form.get("category")
    if not category_name:
        return jsonify({"error": "分类名称是必需的"}), 400

    if category_name == "常用":
        url = request.form.get("url", "").strip()
        if not url:
            return jsonify({"error": "常用项目删除需要提供 url"}), 400
        stats = stats_service.get_visit_stats()
        if url not in stats:
            return jsonify({"error": "项目未找到"}), 404
        stats_service.remove_stat(url)
        return jsonify({"success": True, "message": "项目已删除"})

    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    title = request.form.get("title")

    item = config_service.find_item_in_category(category_name, title)
    if not item:
        return jsonify({"error": "项目未找到"}), 404

    item_url = (item.get("url") or "").strip()
    config_service.remove_item_from_category(category_name, title)

    if item_url:
        stats = stats_service.get_visit_stats()
        if item_url in stats:
            stats_service.remove_stat(item_url)

    return jsonify({"success": True, "message": "项目已删除"})


def handle_reorder_items():
    category_name = request.form.get("category")
    if not category_name:
        return jsonify({"error": "分类名称是必需的"}), 400

    order = request.form.getlist("order[]") or request.form.get("order")

    if isinstance(order, str):
        order_list = [t.strip() for t in order.split(",") if t.strip()]
    elif isinstance(order, list):
        order_list = [t.strip() for t in order if t.strip()]
    else:
        order_list = []

    if not order_list:
        return jsonify({"error": "排序列表不能为空"}), 400

    config_service.reorder_items_in_category(category_name, order_list)
    return jsonify({"success": True, "message": "项目顺序已更新"})


def handle_move_item():
    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400

    category_name = request.form.get("category")
    item_title = request.form.get("title")
    action = request.form.get("action")

    if not config_service.find_item_in_category(category_name, item_title):
        return jsonify({"error": "项目未找到"}), 404

    direction = "up" if action == "move_up" else "down"
    config_service.move_item_in_category(category_name, item_title, direction)

    return jsonify({"success": True, "message": "项目顺序已更新"})


@main_bp.route("/search")
@error_handler
def search():
    search_term = request.args.get("term", "").strip()
    if not search_term:
        return jsonify([])

    search_term_lower = search_term.lower()

    try:
        categories = config_service.get_categories()
        results = []

        for category in categories:
            for item in category.get("items", []):
                title = item.get("title", "")
                url = item.get("url", "")
                title_pinyin = "".join(lazy_pinyin(title)).lower()

                if (
                    search_term_lower in title.lower()
                    or search_term_lower in url.lower()
                    or search_term_lower in title_pinyin
                ):
                    results.append(item)

        return jsonify(results)

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return jsonify([])


@main_bp.route("/api/visit-stats", methods=["GET"])
@error_handler
def get_visit_stats():
    try:
        stats = stats_service.get_visit_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取访问统计失败: {e}")
        return jsonify({}), 500


@main_bp.route("/api/visit-stats/record", methods=["POST"])
@error_handler
def record_visit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400

        url = data.get("url", "").strip()
        title = data.get("title", "").strip()
        icon = data.get("icon", "fas fa-link")

        if not url or not title:
            return jsonify({"error": "url和title是必需的"}), 400

        updated_stat = stats_service.record_visit(url, title, icon)
        return jsonify({"success": True, "data": updated_stat})

    except Exception as e:
        logger.error(f"记录访问失败: {e}")
        return jsonify({"error": "记录访问失败"}), 500
