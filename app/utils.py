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
