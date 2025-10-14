"""
配置管理模块 - 封装配置文件操作
提供文件锁、缓存和错误处理功能
"""
import json
import os
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_project_root() -> str:
    """
    获取项目根目录路径
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 从当前文件位置向上查找项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找包含 pyproject.toml 或 main.py 的目录
    while current_dir != os.path.dirname(current_dir):  # 未到达根目录
        if os.path.exists(os.path.join(current_dir, 'pyproject.toml')) or \
           os.path.exists(os.path.join(current_dir, 'main.py')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # 如果没找到，返回当前目录
    return os.path.dirname(os.path.abspath(__file__))

class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则自动检测
        """
        if config_path is None:
            project_root = get_project_root()
            config_path = os.path.join(project_root, "config", "config.json")
        
        self.config_path = Path(config_path).resolve()
        self.config_dir = self.config_path.parent
        self._lock = threading.RLock()
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 30  # 缓存30秒
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ConfigManager initialized with path: {self.config_path}")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (self._cache is not None and 
                time.time() - self._cache_time < self._cache_ttl)
    
    def load_config(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            use_cache: 是否使用缓存
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON格式错误
            PermissionError: 文件权限错误
        """
        with self._lock:
            # 检查缓存
            if use_cache and self._is_cache_valid():
                return self._cache.copy()
            
            try:
                if not self.config_path.exists():
                    # 创建默认配置
                    default_config = {"categories": []}
                    self._save_config_internal(default_config)
                    return default_config
                
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 更新缓存
                self._cache = config.copy()
                self._cache_time = time.time()
                
                return config
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {self.config_path}, 错误: {e}")
                raise
            except PermissionError as e:
                logger.error(f"文件权限错误: {self.config_path}, 错误: {e}")
                raise
            except Exception as e:
                logger.error(f"加载配置文件失败: {self.config_path}, 错误: {e}")
                raise
    
    def _save_config_internal(self, config: Dict[str, Any]) -> None:
        """内部保存配置方法（不加锁）"""
        # 创建临时文件
        temp_path = self.config_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 原子性替换
            temp_path.replace(self.config_path)
            
            # 更新缓存
            self._cache = config.copy()
            self._cache_time = time.time()
            
        except Exception as e:
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"保存配置文件失败: {self.config_path}, 错误: {e}")
            raise
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            
        Raises:
            PermissionError: 文件权限错误
        """
        with self._lock:
            self._save_config_internal(config)
    
    def update_config(self, updater_func) -> None:
        """
        更新配置文件的原子操作
        
        Args:
            updater_func: 更新函数，接受当前配置，返回更新后的配置
            
        Raises:
            Exception: 更新过程中的任何错误
        """
        with self._lock:
            config = self.load_config(use_cache=False)
            updated_config = updater_func(config)
            self._save_config_internal(updated_config)
    
    def get_categories(self) -> list:
        """获取所有分类"""
        config = self.load_config()
        return config.get("categories", [])
    
    def find_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找分类"""
        categories = self.get_categories()
        for category in categories:
            if category.get("name") == name:
                return category
        return None
    
    def find_item_in_category(self, category_name: str, item_title: str) -> Optional[Dict[str, Any]]:
        """在指定分类中查找项目"""
        category = self.find_category_by_name(category_name)
        if not category:
            return None
        
        items = category.get("items", [])
        for item in items:
            if item.get("title") == item_title:
                return item
        return None
    
    def add_item_to_category(self, category_name: str, item: Dict[str, Any]) -> None:
        """向分类添加项目"""
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    if "items" not in category:
                        category["items"] = []
                    category["items"].append(item)
                    break
            return config
        
        self.update_config(updater)
    
    def update_item_in_category(self, category_name: str, old_title: str, 
                               new_item: Dict[str, Any]) -> None:
        """更新分类中的项目"""
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
        
        self.update_config(updater)
    
    def remove_item_from_category(self, category_name: str, item_title: str) -> None:
        """从分类中删除项目"""
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    category["items"] = [item for item in items 
                                       if item.get("title") != item_title]
                    break
            return config
        
        self.update_config(updater)
    
    def reorder_items_in_category(self, category_name: str, order: list) -> None:
        """重新排序分类中的项目"""
        def updater(config):
            for category in config.get("categories", []):
                if category.get("name") == category_name:
                    items = category.get("items", [])
                    items_map = {item.get("title"): item for item in items}
                    
                    new_items = []
                    for title in order:
                        if title in items_map:
                            new_items.append(items_map.pop(title))
                    
                    # 追加任何未出现在 order 中的剩余项，保持相对顺序
                    for item in items:
                        if item.get("title") in items_map:
                            new_items.append(item)
                    
                    category["items"] = new_items
                    break
            return config
        
        self.update_config(updater)
    
    def move_item_in_category(self, category_name: str, item_title: str, 
                            direction: str) -> None:
        """在分类中移动项目"""
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
        
        self.update_config(updater)
    
    def move_item_between_categories(self, old_category: str, new_category: str, 
                                   item_title: str) -> None:
        """在分类间移动项目"""
        def updater(config):
            item_to_move = None
            
            # 从原分类移除
            for category in config.get("categories", []):
                if category.get("name") == old_category:
                    items = category.get("items", [])
                    for i, item in enumerate(items):
                        if item.get("title") == item_title:
                            item_to_move = items.pop(i)
                            break
                    break
            
            # 添加到新分类
            if item_to_move:
                for category in config.get("categories", []):
                    if category.get("name") == new_category:
                        if "items" not in category:
                            category["items"] = []
                        category["items"].append(item_to_move)
                        break
            
            return config
        
        self.update_config(updater)
    
    def invalidate_cache(self) -> None:
        """使缓存失效"""
        with self._lock:
            self._cache = None
            self._cache_time = 0


# 全局配置管理器实例
config_manager = ConfigManager()
