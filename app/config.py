"""
应用配置管理模块
统一管理所有配置相关的设置和路径
"""
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AppConfig:
    """应用配置类"""
    
    def __init__(self):
        """初始化应用配置"""
        self._detect_environment()
        self._setup_paths()
        self._setup_logging()
    
    def _detect_environment(self):
        """检测运行环境"""
        # 检测是否在Docker容器中运行
        self.is_docker = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER') == 'true'
        
        # 检测是否在开发环境
        self.is_development = os.environ.get('FLASK_ENV') == 'development' or \
                             os.environ.get('ENVIRONMENT') == 'development'
        
        # 设置环境名称
        if self.is_docker:
            self.environment = 'docker'
        elif self.is_development:
            self.environment = 'development'
        else:
            self.environment = 'production'
        
        logger.info(f"Environment detected: {self.environment}")
    
    def _setup_paths(self):
        """设置各种路径"""
        if self.is_docker:
            # Docker环境路径
            self.base_dir = Path('/app')
            self.config_dir = Path('/config')
            self.data_dir = Path('/config')
        else:
            # 本地环境路径
            self.base_dir = self._find_project_root()
            self.config_dir = self.base_dir / 'config'
            self.data_dir = self.base_dir / 'config'
        
        # 具体文件路径
        self.config_file = self.config_dir / 'config.json'
        self.images_dir = self.data_dir / 'img'
        
        # 确保目录存在
        self._ensure_directories()
        
        logger.info(f"Base directory: {self.base_dir}")
        logger.info(f"Config file: {self.config_file}")
        logger.info(f"Images directory: {self.images_dir}")
    
    def _find_project_root(self) -> Path:
        """查找项目根目录"""
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent
        
        # 向上查找包含项目标识文件的目录
        for parent in current_dir.parents:
            if any((parent / marker).exists() for marker in ['pyproject.toml', 'main.py', '.git']):
                return parent
        
        # 如果没找到，返回当前目录的父目录
        return current_dir.parent
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not self.is_docker:
            # 仅在非Docker环境创建目录
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """设置日志配置"""
        import time
        
        # 设置时区
        timezone = os.environ.get('TZ', 'Asia/Shanghai')
        
        # 设置时区环境变量
        os.environ['TZ'] = timezone
        
        # 重新加载时间模块以应用时区
        if hasattr(time, 'tzset'):
            time.tzset()
        
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        
        if self.is_development:
            # 开发环境使用更详细的日志
            logging.basicConfig(
                level=getattr(logging, log_level, logging.INFO),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # 生产环境使用简洁的日志格式
            logging.basicConfig(
                level=getattr(logging, log_level, logging.WARNING),
                format='%(levelname)s: %(message)s'
            )
    
    @property
    def config_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_file)
    
    @property
    def images_path(self) -> str:
        """获取图片目录路径"""
        return str(self.images_dir)
    
    @property
    def debug(self) -> bool:
        """是否启用调试模式"""
        return self.is_development or os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    @property
    def host(self) -> str:
        """获取监听主机"""
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def port(self) -> int:
        """获取监听端口"""
        return int(os.environ.get('PORT', '8080'))
    
    @property
    def max_content_length(self) -> int:
        """获取最大上传文件大小（字节）"""
        return int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    @property
    def cache_ttl(self) -> int:
        """获取缓存TTL（秒）"""
        return int(os.environ.get('CACHE_TTL', '30'))
    
    @property
    def timezone(self) -> str:
        """获取时区设置"""
        return os.environ.get('TZ', 'Asia/Shanghai')
    
    def get_static_url(self, filename: str) -> str:
        """获取静态文件URL"""
        if self.is_docker:
            return f'/config/img/{filename}'
        else:
            return f'/config/img/{filename}'
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            # 检查配置文件是否存在或可创建
            if not self.config_file.exists():
                if self.is_docker:
                    logger.error(f"Config file not found: {self.config_file}")
                    return False
                else:
                    logger.info(f"Creating default config file: {self.config_file}")
                    self._create_default_config()
            
            # 检查图片目录是否存在
            if not self.images_dir.exists():
                if self.is_docker:
                    logger.error(f"Images directory not found: {self.images_dir}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False
    
    def _create_default_config(self):
        """创建默认配置文件"""
        import json
        
        default_config = {
            "categories": []
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info("Default config file created")

# 全局配置实例
config = AppConfig()
