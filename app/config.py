"""
应用配置管理模块
统一管理所有配置相关的设置和路径
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class AppConfig:
    """应用配置类"""

    def __init__(self) -> None:
        """初始化应用配置"""
        self.is_docker: bool = False
        self.is_development: bool = False
        self.environment: str = "production"
        self.base_dir: Path = Path()
        self.config_dir: Path = Path()
        self.data_dir: Path = Path()
        self.db_file: Path = Path()
        self.images_dir: Path = Path()

        self._detect_environment()
        self._setup_paths()
        self._setup_logging()

    def _detect_environment(self) -> None:
        """检测运行环境"""
        self.is_docker = (
            os.path.exists("/.dockerenv")
            or os.environ.get("DOCKER_CONTAINER") == "true"
        )

        self.is_development = (
            os.environ.get("FLASK_ENV") == "development"
            or os.environ.get("ENVIRONMENT") == "development"
        )

        if self.is_docker:
            self.environment = "docker"
        elif self.is_development:
            self.environment = "development"
        else:
            self.environment = "production"

        logger.info(f"Environment detected: {self.environment}")

    def _setup_paths(self) -> None:
        """设置各种路径"""
        if self.is_docker:
            self.base_dir = Path("/app")
            self.config_dir = Path("/config")
            self.data_dir = Path("/config")
        else:
            self.base_dir = self._find_project_root()
            self.config_dir = self.base_dir / "config"
            self.data_dir = self.base_dir / "config"

        self.db_file = self.config_dir / "homer.db"
        self.images_dir = self.data_dir / "img"

        self._ensure_directories()

        logger.info(f"Base directory: {self.base_dir}")
        logger.info(f"Database: {self.db_file}")
        logger.info(f"Images directory: {self.images_dir}")

    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent

        for parent in current_dir.parents:
            if any(
                (parent / marker).exists()
                for marker in ["pyproject.toml", "main.py", ".git"]
            ):
                return parent

        return current_dir.parent

    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        if not self.is_docker:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.images_dir.mkdir(parents=True, exist_ok=True)

        self.db_file.parent.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        """设置日志配置"""
        import time

        timezone = os.environ.get("TZ", "Asia/Shanghai")
        os.environ["TZ"] = timezone

        if hasattr(time, "tzset"):
            time.tzset()

        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

        if self.is_development:
            logging.basicConfig(
                level=getattr(logging, log_level, logging.INFO),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            logging.basicConfig(
                level=getattr(logging, log_level, logging.WARNING),
                format="%(levelname)s: %(message)s",
            )

    @property
    def db_path(self) -> str:
        """获取数据库文件路径"""
        return str(self.db_file)

    @property
    def images_path(self) -> str:
        """获取图片目录路径"""
        return str(self.images_dir)

    @property
    def debug(self) -> bool:
        """是否启用调试模式"""
        return (
            self.is_development
            or os.environ.get("FLASK_DEBUG", "false").lower() == "true"
        )

    @property
    def host(self) -> str:
        """获取监听主机"""
        return os.environ.get("HOST", "0.0.0.0")

    @property
    def port(self) -> int:
        """获取监听端口"""
        return int(os.environ.get("PORT", "8080"))

    @property
    def max_content_length(self) -> int:
        """获取最大上传文件大小（字节）"""
        return int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    @property
    def cache_ttl(self) -> int:
        """获取缓存TTL（秒）"""
        return int(os.environ.get("CACHE_TTL", "30"))

    @property
    def timezone(self) -> str:
        """获取时区设置"""
        return os.environ.get("TZ", "Asia/Shanghai")

    def get_static_url(self, filename: str) -> str:
        """获取静态文件URL"""
        return f"/config/img/{filename}"


config: AppConfig = AppConfig()
