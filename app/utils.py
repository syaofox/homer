"""
工具函数模块 - 提供通用功能
包括输入验证、路径处理、错误处理等
"""
import json
import re
import os
from typing import Any, Optional, Dict, List
from functools import wraps
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Font Awesome 5 图标到内联 SVG 的映射（用于替代 CDN，实现首屏秒开）
# 图标路径来自 Font Awesome Free 5.15.4，CC BY 4.0
_ICON_SVG_MAP = {
    'eye': ('0 0 576 512', 'M572.52 241.4C518.29 135.59 410.93 64 288 64S57.68 135.64 3.48 241.41a32.35 32.35 0 0 0 0 29.19C57.71 376.41 165.07 448 288 448s230.32-71.64 284.52-177.41a32.35 32.35 0 0 0 0-29.19zM288 400a144 144 0 1 1 144-144 143.93 143.93 0 0 1-144 144zm0-240a95.31 95.31 0 0 0-25.31 3.79 47.85 47.85 0 0 1-66.9 66.9A95.78 95.78 0 1 0 288 160z'),
    'eye-slash': ('0 0 640 512', 'M320 400c-75.85 0-137.25-58.71-142.9-133.11L72.2 185.82c-13.79 17.3-26.48 35.59-36.72 55.59a32.35 32.35 0 0 0 0 29.19C89.71 376.41 197.07 448 320 448c26.91 0 52.87-4 77.89-10.46L346 397.39a144.13 144.13 0 0 1-26 2.61zm313.82 58.1l-110.55-85.44a331.25 331.25 0 0 0 81.25-102.07 32.35 32.35 0 0 0 0-29.19C550.29 135.59 442.93 64 320 64a308.15 308.15 0 0 0-147.32 37.7L45.46 3.37A16 16 0 0 0 23 6.18L3.37 31.45A16 16 0 0 0 6.18 53.9l588.36 454.73a16 16 0 0 0 22.46-2.81l19.64-25.27a16 16 0 0 0-2.82-22.45zm-183.72-142l-39.3-30.38A94.75 94.75 0 0 0 416 256a94.76 94.76 0 0 0-121.31-92.21A47.65 47.65 0 0 1 304 192a46.64 46.64 0 0 1-1.54 10l-73.61-56.89A142.31 142.31 0 0 1 320 112a143.92 143.92 0 0 1 144 144c0 21.63-5.29 41.79-13.9 60.11z'),
    'plus': ('0 0 448 512', 'M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z'),
    'link': ('0 0 512 512', 'M326.612 185.391c59.747 59.809 58.927 155.698.36 214.59-.11.12-.24.25-.36.37l-67.2 67.2c-59.27 59.27-155.699 59.262-214.96 0-59.27-59.26-59.27-155.7 0-214.96l37.106-37.106c9.84-9.84 26.786-3.3 27.294 10.606.648 17.722 3.826 35.527 9.69 52.721 1.986 5.822.567 12.262-3.783 16.612l-13.087 13.087c-28.026 28.026-28.905 73.66-1.155 101.96 28.024 28.579 74.086 28.749 102.325.51l67.2-67.19c28.191-28.191 28.073-73.757 0-101.83-3.701-3.694-7.429-6.564-10.341-8.569a16.037 16.037 0 0 1-6.947-12.606c-.396-10.567 3.348-21.456 11.698-29.806l21.054-21.055c5.521-5.521 14.182-6.199 20.584-1.731a152.482 152.482 0 0 1 20.522 17.197zM467.547 44.449c-59.261-59.262-155.69-59.27-214.96 0l-67.2 67.2c-.12.12-.25.25-.36.37-58.566 58.892-59.387 154.781.36 214.59a152.454 152.454 0 0 0 20.521 17.196c6.402 4.468 15.064 3.789 20.584-1.731l21.054-21.055c8.35-8.35 12.094-19.239 11.698-29.806a16.037 16.037 0 0 0-6.947-12.606c-2.912-2.005-6.64-4.875-10.341-8.569-28.073-28.073-28.191-73.639 0-101.83l67.2-67.19c28.239-28.239 74.3-28.069 102.325.51 27.75 28.3 26.872 73.934-1.155 101.96l-13.087 13.087c-4.35 4.35-5.769 10.79-3.783 16.612 5.864 17.194 9.042 34.999 9.69 52.721.509 13.906 17.454 20.446 27.294 10.606l37.106-37.106c59.271-59.259 59.271-155.699.001-214.959z'),
    'robot': ('0 0 640 512', 'M32,224H64V416H32A31.96166,31.96166,0,0,1,0,384V256A31.96166,31.96166,0,0,1,32,224Zm512-48V448a64.06328,64.06328,0,0,1-64,64H160a64.06328,64.06328,0,0,1-64-64V176a79.974,79.974,0,0,1,80-80H288V32a32,32,0,0,1,64,0V96H464A79.974,79.974,0,0,1,544,176ZM264,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,264,256Zm-8,128H192v32h64Zm96,0H288v32h64ZM456,256a40,40,0,1,0-40,40A39.997,39.997,0,0,0,456,256Zm-8,128H384v32h64ZM640,256V384a31.96166,31.96166,0,0,1-32,32H576V224h32A31.96166,31.96166,0,0,1,640,256Z'),
    'server': ('0 0 512 512', 'M480 160H32c-17.673 0-32-14.327-32-32V64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm112 248H32c-17.673 0-32-14.327-32-32v-64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm112 248H32c-17.673 0-32-14.327-32-32v-64c0-17.673 14.327-32 32-32h448c17.673 0 32 14.327 32 32v64c0 17.673-14.327 32-32 32zm-48-88c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24zm-64 0c-13.255 0-24 10.745-24 24s10.745 24 24 24 24-10.745 24-24-10.745-24-24-24z'),
}


def is_fa_icon(icon_path: str) -> bool:
    """
    判断图标路径是否为 Font Awesome 类名（用于 SVG 渲染），而非自定义图片路径。

    支持格式：fas fa-eye、fab fa-xxx、far fa-xxx、fal fa-xxx、fa fa-server 等。
    自定义图片路径以 img/ 开头，返回 False。

    Args:
        icon_path: 图标路径或 Font Awesome 类名

    Returns:
        bool: 若为 FA 类名返回 True，否则（如图片路径）返回 False
    """
    if not icon_path or not isinstance(icon_path, str):
        return False
    icon_path = icon_path.strip()
    return icon_path.startswith(('fas ', 'fab ', 'far ', 'fal ', 'fa '))


def icon_to_svg(icon_class: str, css_class: str = "icon-svg") -> str:
    """
    将 Font Awesome 图标类名映射为内联 SVG 片段，用于替代 CDN 字体图标。

    支持格式：fas fa-eye、fa fa-server、fa-eye 等。
    无法识别的图标将回退为 fa-link。

    Args:
        icon_class: Font Awesome 图标类名，如 "fas fa-eye"、"fa fa-server"
        css_class: 输出 SVG 的 class 属性，默认 "icon-svg"

    Returns:
        str: 内联 SVG 的 HTML 字符串，可直接插入模板

    Example:
        {{ icon_to_svg('fas fa-eye')|safe }}
    """
    if not icon_class or not isinstance(icon_class, str):
        icon_class = "fa-link"
    icon_class = icon_class.strip()
    # 提取图标名：fas fa-eye -> eye, fa fa-server -> server, fa-eye -> eye
    parts = icon_class.split()
    icon_name = None
    for p in parts:
        if p.startswith("fa-") and len(p) > 3:
            icon_name = p[3:]  # 去掉 "fa-"
            break
    if not icon_name:
        icon_name = "link"
    viewbox, path_d = _ICON_SVG_MAP.get(icon_name, _ICON_SVG_MAP["link"])
    return (
        f'<svg class="{css_class}" aria-hidden="true" viewBox="{viewbox}" '
        f'xmlns="http://www.w3.org/2000/svg"><path d="{path_d}"/></svg>'
    )


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: 要验证的URL字符串
        
    Returns:
        bool: URL格式是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_title(title: str) -> bool:
    """
    验证标题格式
    
    Args:
        title: 要验证的标题字符串
        
    Returns:
        bool: 标题格式是否有效
    """
    if not title or not isinstance(title, str):
        return False
    
    # 去除首尾空格
    title = title.strip()
    
    # 检查长度
    if len(title) == 0 or len(title) > 100:
        return False
    
    # 检查是否包含危险字符
    dangerous_chars = ['<', '>', '"', "'", '&']
    if any(char in title for char in dangerous_chars):
        return False
    
    return True

def validate_category_name(category_name: str) -> bool:
    """
    验证分类名称格式
    
    Args:
        category_name: 要验证的分类名称
        
    Returns:
        bool: 分类名称格式是否有效
    """
    if not category_name or not isinstance(category_name, str):
        return False
    
    category_name = category_name.strip()
    
    # 检查长度
    if len(category_name) == 0 or len(category_name) > 50:
        return False
    
    # 检查是否包含危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '/', '\\']
    if any(char in category_name for char in dangerous_chars):
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    if not filename:
        return ""
    
    # 移除路径分隔符和危险字符
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # 限制长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def validate_icon_path(icon_path: str) -> bool:
    """
    验证图标路径格式
    
    Args:
        icon_path: 图标路径
        
    Returns:
        bool: 图标路径是否有效
    """
    if not icon_path or not isinstance(icon_path, str):
        return False
    
    # FontAwesome 图标格式
    if icon_path.startswith(('fas ', 'fab ', 'far ', 'fal ', 'fa ')):
        return True
    
    # 自定义图片路径格式
    if icon_path.startswith('img/'):
        filename = icon_path[4:]  # 移除 'img/' 前缀
        return validate_image_filename(filename)
    
    return False

def validate_image_filename(filename: str) -> bool:
    """
    验证图片文件名格式
    
    Args:
        filename: 图片文件名
        
    Returns:
        bool: 文件名是否有效
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # 检查文件扩展名
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp'}
    _, ext = os.path.splitext(filename.lower())
    if ext not in allowed_extensions:
        return False
    
    # 检查文件名长度
    if len(filename) > 255:
        return False
    
    # 检查是否包含危险字符
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in filename for char in dangerous_chars):
        return False
    
    return True

def validate_form_data(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    验证表单数据
    
    Args:
        data: 表单数据字典
        required_fields: 必需字段列表
        
    Returns:
        Dict[str, Any]: 验证结果，包含 'valid' 和 'errors' 键
        
    Example:
        result = validate_form_data(request.form, ['title', 'url'])
        if not result['valid']:
            return jsonify({'error': result['errors']}), 400
    """
    errors = {}
    
    # 检查必需字段
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"字段 '{field}' 是必需的"
    
    # 验证具体字段
    if 'title' in data and data['title']:
        if not validate_title(data['title']):
            errors['title'] = "标题格式无效"
    
    if 'url' in data and data['url']:
        if not validate_url(data['url']):
            errors['url'] = "URL格式无效"
    
    if 'category' in data and data['category']:
        if not validate_category_name(data['category']):
            errors['category'] = "分类名称格式无效"
    
    if 'new_category' in data and data['new_category']:
        if not validate_category_name(data['new_category']):
            errors['new_category'] = "新分类名称格式无效"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def error_handler(f):
    """
    错误处理装饰器
    捕获异常并返回适当的错误响应
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"文件未找到: {e}")
            return {'error': '配置文件未找到'}, 404
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return {'error': '配置文件格式错误'}, 500
        except PermissionError as e:
            logger.error(f"权限错误: {e}")
            return {'error': '文件权限不足'}, 403
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return {'error': '服务器内部错误'}, 500
    return decorated_function


def clean_html_content(content: str) -> str:
    """
    清理HTML内容，移除潜在的危险标签
    
    Args:
        content: 原始HTML内容
        
    Returns:
        str: 清理后的安全内容
    """
    if not content:
        return ""
    
    # 移除HTML标签
    clean = re.sub(r'<[^>]+>', '', content)
    
    # 转义特殊字符
    clean = clean.replace('&', '&amp;')
    clean = clean.replace('<', '&lt;')
    clean = clean.replace('>', '&gt;')
    clean = clean.replace('"', '&quot;')
    clean = clean.replace("'", '&#x27;')
    
    return clean

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def format_error_message(errors: Dict[str, str]) -> str:
    """
    格式化错误消息
    
    Args:
        errors: 错误字典
        
    Returns:
        str: 格式化的错误消息
    """
    if not errors:
        return ""
    
    if len(errors) == 1:
        return list(errors.values())[0]
    
    return "多个错误: " + "; ".join(errors.values())
