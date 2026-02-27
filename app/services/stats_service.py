import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.core.base_manager import BaseManager
from app.config import config as app_config


class StatsService(BaseManager):
    """访问统计服务"""

    def __init__(self):
        config_dir = Path(app_config.config_dir)
        super().__init__(config_dir / "visit_stats.json", app_config.cache_ttl)

    def _get_default_data(self) -> Dict[str, Any]:
        return {}

    def get_visit_stats(self) -> Dict[str, Any]:
        return self.load()

    def record_visit(self, url: str, title: str, icon: str) -> Dict[str, Any]:
        stats = self.load(use_cache=False)
        current_time = int(time.time() * 1000)

        if url not in stats:
            stats[url] = {
                "title": title,
                "icon": icon,
                "url": url,
                "count": 0,
                "lastVisit": current_time,
            }

        stats[url]["count"] += 1
        stats[url]["lastVisit"] = current_time
        stats[url]["title"] = title
        stats[url]["icon"] = icon

        self._save_internal(stats)
        return stats[url]

    def get_top_visited(self, limit: int = 20) -> List[Dict[str, Any]]:
        stats = self.load()
        sites = list(stats.values())
        sites.sort(key=lambda x: x.get("count", 0), reverse=True)
        return sites[:limit]

    def remove_stat(self, url: str) -> None:
        stats = self.load(use_cache=False)
        if url in stats:
            del stats[url]
            self._save_internal(stats)

    def update_stat(
        self, old_url: str, new_url: str, title: str, icon: str
    ) -> Optional[Dict[str, Any]]:
        stats = self.load(use_cache=False)
        if old_url not in stats:
            return None

        entry = stats[old_url]
        if old_url == new_url:
            entry["title"] = title
            entry["icon"] = icon
            entry["url"] = new_url
            self._save_internal(stats)
            return entry

        entry["title"] = title
        entry["icon"] = icon
        entry["url"] = new_url
        stats[new_url] = entry
        del stats[old_url]
        self._save_internal(stats)
        return entry


stats_service = StatsService()
