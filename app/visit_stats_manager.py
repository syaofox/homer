"""
访问统计管理模块 - 封装访问统计数据操作
提供文件锁、缓存和错误处理功能
"""
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from .config import config as app_config

logger = logging.getLogger(__name__)

class VisitStatsManager:
    """访问统计管理器"""
    
    def __init__(self):
        """初始化访问统计管理器"""
        self.config_dir = Path(app_config.config_dir)
        self.stats_path = self.config_dir / "visit_stats.json"
        self._lock = threading.RLock()
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = app_config.cache_ttl
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VisitStatsManager initialized with path: {self.stats_path}")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (self._cache is not None and 
                time.time() - self._cache_time < self._cache_ttl)
    
    def load_stats(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载访问统计数据
        
        Args:
            use_cache: 是否使用缓存
            
        Returns:
            访问统计字典，格式: {url: {title, icon, url, count, lastVisit}}
        """
        with self._lock:
            # 检查缓存
            if use_cache and self._is_cache_valid():
                return self._cache.copy()
            
            try:
                if not self.stats_path.exists():
                    # 创建默认空统计数据
                    default_stats = {}
                    self._save_stats_internal(default_stats)
                    return default_stats
                
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                # 更新缓存
                self._cache = stats.copy()
                self._cache_time = time.time()
                
                return stats
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {self.stats_path}, 错误: {e}")
                # 返回空统计数据
                return {}
            except Exception as e:
                logger.error(f"加载访问统计失败: {self.stats_path}, 错误: {e}")
                return {}
    
    def _save_stats_internal(self, stats: Dict[str, Any]) -> None:
        """内部保存统计数据方法（不加锁）"""
        # 创建临时文件
        temp_path = self.stats_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            # 原子性替换
            temp_path.replace(self.stats_path)
            
            # 更新缓存
            self._cache = stats.copy()
            self._cache_time = time.time()
            
        except Exception as e:
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"保存访问统计失败: {self.stats_path}, 错误: {e}")
            raise
    
    def save_stats(self, stats: Dict[str, Any]) -> None:
        """
        保存访问统计数据
        
        Args:
            stats: 访问统计字典
        """
        with self._lock:
            self._save_stats_internal(stats)
    
    def get_visit_stats(self) -> Dict[str, Any]:
        """获取所有访问统计数据"""
        return self.load_stats()
    
    def record_visit(self, url: str, title: str, icon: str) -> Dict[str, Any]:
        """
        记录一次访问
        
        Args:
            url: 访问的URL
            title: 站点标题
            icon: 站点图标
            
        Returns:
            更新后的该站点统计数据
        """
        with self._lock:
            stats = self.load_stats(use_cache=False)
            
            if url not in stats:
                stats[url] = {
                    'title': title,
                    'icon': icon,
                    'url': url,
                    'count': 0,
                    'lastVisit': int(time.time() * 1000)  # 毫秒时间戳
                }
            
            stats[url]['count'] += 1
            stats[url]['lastVisit'] = int(time.time() * 1000)
            
            # 更新标题和图标（可能已改变）
            stats[url]['title'] = title
            stats[url]['icon'] = icon
            
            self._save_stats_internal(stats)
            
            return stats[url]
    
    def get_top_visited(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取访问频率最高的站点

        Args:
            limit: 返回的站点数量限制

        Returns:
            按访问次数排序的站点列表
        """
        stats = self.load_stats()
        sites = list(stats.values())

        # 按访问次数降序排序
        sites.sort(key=lambda x: x.get('count', 0), reverse=True)

        return sites[:limit]

    def remove_stat(self, url: str) -> None:
        """
        按 URL 删除一条访问统计

        Args:
            url: 要删除的站点 URL
        """
        with self._lock:
            stats = self.load_stats(use_cache=False)
            if url in stats:
                del stats[url]
                self._save_stats_internal(stats)

    def update_stat(
        self,
        old_url: str,
        new_url: str,
        title: str,
        icon: str,
    ) -> Optional[Dict[str, Any]]:
        """
        更新一条访问统计（支持修改 URL）

        Args:
            old_url: 原 URL（用于定位）
            new_url: 新 URL
            title: 新标题
            icon: 新图标

        Returns:
            更新后的该条统计，若原记录不存在则返回 None
        """
        with self._lock:
            stats = self.load_stats(use_cache=False)
            if old_url not in stats:
                return None
            entry = stats[old_url]
            if old_url == new_url:
                entry["title"] = title
                entry["icon"] = icon
                entry["url"] = new_url
                self._save_stats_internal(stats)
                return entry
            # URL 变更：保留 count、lastVisit，用新 key 写入后删除旧 key
            entry["title"] = title
            entry["icon"] = icon
            entry["url"] = new_url
            stats[new_url] = entry
            del stats[old_url]
            self._save_stats_internal(stats)
            return entry

    def invalidate_cache(self) -> None:
        """使缓存失效"""
        with self._lock:
            self._cache = None
            self._cache_time = 0


# 全局访问统计管理器实例
visit_stats_manager = VisitStatsManager()

