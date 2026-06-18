import os
from typing import Any
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return False
    try:
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def validate_title(title: str) -> bool:
    """验证标题格式"""
    if not title or not isinstance(title, str):
        return False
    title = title.strip()
    if len(title) == 0 or len(title) > 100:
        return False
    dangerous_chars = ["<", ">", '"', "'", "&"]
    return not any(char in title for char in dangerous_chars)


def validate_category_name(category_name: str) -> bool:
    """验证分类名称格式"""
    if not category_name or not isinstance(category_name, str):
        return False
    category_name = category_name.strip()
    if len(category_name) == 0 or len(category_name) > 50:
        return False
    dangerous_chars = ["<", ">", '"', "'", "&", "/", "\\"]
    return not any(char in category_name for char in dangerous_chars)


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除危险字符"""
    if not filename:
        return ""
    dangerous_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext
    return filename


def validate_icon_path(icon_path: str) -> bool:
    """验证图标路径格式"""
    if not icon_path or not isinstance(icon_path, str):
        return False
    if icon_path.startswith(("fas ", "fab ", "far ", "fal ", "fa ")):
        return True
    if icon_path.startswith("img/"):
        filename = icon_path[4:]
        return validate_image_filename(filename)
    return False


def validate_image_filename(filename: str) -> bool:
    """验证图片文件名格式"""
    if not filename or not isinstance(filename, str):
        return False
    allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"}
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed_extensions:
        return False
    if len(filename) > 255:
        return False
    dangerous_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    return not any(char in filename for char in dangerous_chars)


def validate_form_data(
    data: dict[str, Any], required_fields: list[str]
) -> dict[str, Any]:
    """验证表单数据"""
    errors: dict[str, str] = {}
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"字段 '{field}' 是必需的"

    if "title" in data and data["title"]:
        if not validate_title(str(data["title"])):
            errors["title"] = "标题格式无效"

    if "url" in data and data["url"]:
        if not validate_url(str(data["url"])):
            errors["url"] = "URL格式无效"

    if "category" in data and data["category"]:
        if not validate_category_name(str(data["category"])):
            errors["category"] = "分类名称格式无效"

    if "new_category" in data and data["new_category"]:
        if not validate_category_name(str(data["new_category"])):
            errors["new_category"] = "新分类名称格式无效"

    return {"valid": len(errors) == 0, "errors": errors}


def format_error_message(errors: dict[str, str]) -> str:
    """格式化错误消息"""
    if not errors:
        return ""
    if len(errors) == 1:
        return list(errors.values())[0]
    return "多个错误: " + "; ".join(errors.values())
