import json
import os
import logging
from pypinyin import lazy_pinyin

from flask import redirect, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename

from app import app
from app.config_manager import config_manager
from app.config import config as app_config
from app.utils import (
    validate_form_data, error_handler,
    validate_title, validate_url, validate_category_name,
    sanitize_filename, format_error_message
)

# 设置日志
logger = logging.getLogger(__name__)

CONFIG_IMG_PATH = app_config.images_path

@app.route("/")
@error_handler
def index():
    """主页 - 显示导航分类"""
    try:
        categories = config_manager.get_categories()
        categories_data = [
            {"name": category["name"], "nav_items": category["items"]}
            for category in categories
        ]
        return render_template("index.html", categories=categories_data)
    except Exception as e:
        logger.error(f"加载主页失败: {e}")
        return render_template("index.html", categories=[])


@app.route("/config", methods=["GET", "POST"])
@error_handler
def config():
    """配置管理页面"""
    if request.method == "POST":
        return handle_config_post()
    
    try:
        categories = config_manager.get_categories()
        categories_data = [
            {"name": category["name"], "nav_items": category["items"]}
            for category in categories
        ]
        return render_template("config.html", categories=categories_data)
    except Exception as e:
        logger.error(f"加载配置页面失败: {e}")
        return render_template("config.html", categories=[])

def handle_config_post():
    """处理配置页面的POST请求"""
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
    """处理添加项目"""
    # 验证输入数据
    validation = validate_form_data(request.form, ["category", "title", "url"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400
    
    category = request.form.get("category")
    title = request.form.get("title")
    url = request.form.get("url")
    icon = request.files.get("icon")

    # 处理图标
    if icon and icon.filename:
        filename = sanitize_filename(secure_filename(icon.filename))
        if not filename:
            return jsonify({"error": "无效的文件名"}), 400
        
        icon.save(os.path.join(CONFIG_IMG_PATH, filename))
        icon_path = f"img/{filename}"
    else:
        icon_path = "fas fa-link"

    # 添加项目
    new_item = {"title": title, "icon": icon_path, "url": url}
    config_manager.add_item_to_category(category, new_item)
    
    return jsonify({"success": True, "message": "项目已添加"})

def handle_edit_item():
    """处理编辑项目"""
    # 验证输入数据
    validation = validate_form_data(request.form, ["old_category", "old_title", "new_category", "new_title", "new_url"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400
    
    old_category = request.form.get("old_category")
    new_category = request.form.get("new_category")
    old_title = request.form.get("old_title")
    new_title = request.form.get("new_title")
    new_url = request.form.get("new_url")
    new_icon = request.files.get("new_icon")

    # 处理新图标
    icon_path = None
    if new_icon and new_icon.filename:
        filename = sanitize_filename(secure_filename(new_icon.filename))
        if filename:
            new_icon.save(os.path.join(CONFIG_IMG_PATH, filename))
            icon_path = f"img/{filename}"

    # 获取原项目信息
    original_item = config_manager.find_item_in_category(old_category, old_title)
    if not original_item:
        return jsonify({"error": "项目未找到"}), 404

    # 创建更新后的项目
    updated_item = {
        "title": new_title,
        "url": new_url,
        "icon": icon_path if icon_path else original_item["icon"]
    }

    if old_category == new_category:
        # 同一分类内更新
        config_manager.update_item_in_category(old_category, old_title, updated_item)
    else:
        # 跨分类更新 - 先删除再添加
        config_manager.remove_item_from_category(old_category, old_title)
        config_manager.add_item_to_category(new_category, updated_item)
    
    return jsonify({"success": True, "message": "项目已更新"})

def handle_delete_item():
    """处理删除项目"""
    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400
    
    category_name = request.form.get("category")
    title = request.form.get("title")

    # 检查项目是否存在
    if not config_manager.find_item_in_category(category_name, title):
        return jsonify({"error": "项目未找到"}), 404

    config_manager.remove_item_from_category(category_name, title)
    return jsonify({"success": True, "message": "项目已删除"})

def handle_reorder_items():
    """处理重新排序项目"""
    category_name = request.form.get("category")
    if not category_name:
        return jsonify({"error": "分类名称是必需的"}), 400
    
    order = request.form.getlist("order[]") or request.form.get("order")
    
    # 支持逗号分隔字符串或多值数组
    if isinstance(order, str):
        order_list = [t.strip() for t in order.split(',') if t.strip()]
    elif isinstance(order, list):
        order_list = [t.strip() for t in order if t.strip()]
    else:
        order_list = []

    if not order_list:
        return jsonify({"error": "排序列表不能为空"}), 400

    config_manager.reorder_items_in_category(category_name, order_list)
    return jsonify({"success": True, "message": "项目顺序已更新"})

def handle_move_item():
    """处理移动项目"""
    validation = validate_form_data(request.form, ["category", "title"])
    if not validation["valid"]:
        return jsonify({"error": format_error_message(validation["errors"])}), 400
    
    category_name = request.form.get("category")
    item_title = request.form.get("title")
    action = request.form.get("action")

    # 检查项目是否存在
    if not config_manager.find_item_in_category(category_name, item_title):
        return jsonify({"error": "项目未找到"}), 404

    direction = "up" if action == "move_up" else "down"
    config_manager.move_item_in_category(category_name, item_title, direction)
    
    return jsonify({"success": True, "message": "项目顺序已更新"})


@app.route('/search')
@error_handler
def search():
    """搜索功能 - 支持中文、拼音和URL搜索"""
    search_term = request.args.get('term', '').strip()
    
    if not search_term:
        return jsonify([])
    
    search_term_lower = search_term.lower()
    
    try:
        categories = config_manager.get_categories()
        results = []
        
        for category in categories:
            for item in category.get('items', []):
                title = item.get('title', '')
                url = item.get('url', '')
                
                # 生成拼音
                title_pinyin = ''.join(lazy_pinyin(title)).lower()
                
                # 搜索匹配逻辑（移除冗余的正则匹配）
                if (search_term_lower in title.lower() or 
                    search_term_lower in url.lower() or 
                    search_term_lower in title_pinyin):
                    results.append(item)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return jsonify([])
