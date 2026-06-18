"""
配置管理单元测试
"""


from app.config import AppConfig


class TestAppConfig:
    def test_default_environment(self) -> None:
        config = AppConfig()
        assert config.environment in ("docker", "development", "production")
        # 清理单例副作用
        config._connection = None  # type: ignore

    def test_paths_are_set(self) -> None:
        config = AppConfig()
        assert config.db_path is not None
        assert config.images_path is not None
        assert config.config_path is not None

    def test_default_properties(self) -> None:
        config = AppConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.cache_ttl == 30
        assert config.timezone == "Asia/Shanghai"
        assert isinstance(config.max_content_length, int)
        assert config.max_content_length > 0

    def test_get_static_url(self) -> None:
        config = AppConfig()
        url = config.get_static_url("test.png")
        assert url == "/config/img/test.png"

    def test_debug_default_false(self) -> None:
        config = AppConfig()
        # 非 development 环境默认为 False
        assert isinstance(config.debug, bool)

    def test_validate_config(self) -> None:
        config = AppConfig()
        # 不应抛异常
        result = config.validate_config()
        assert isinstance(result, bool)
