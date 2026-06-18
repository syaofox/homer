"""
工具函数单元测试
"""

from app.utils import (
    clean_html_content,
    get_version,
    icon_to_svg,
    is_fa_icon,
    truncate_text,
)


class TestGetVersion:
    def test_version_not_empty(self) -> None:
        version = get_version()
        assert version is not None
        assert version != ""

    def test_version_format(self) -> None:
        version = get_version()
        # 应为 semver 格式或 "unknown"
        assert version == "unknown" or len(version.split(".")) == 3


class TestIsFaIcon:
    def test_fas_format(self) -> None:
        assert is_fa_icon("fas fa-eye") is True

    def test_fab_format(self) -> None:
        assert is_fa_icon("fab fa-github") is True

    def test_far_format(self) -> None:
        assert is_fa_icon("far fa-star") is True

    def test_fal_format(self) -> None:
        assert is_fa_icon("fal fa-lightbulb") is True

    def test_fa_format(self) -> None:
        assert is_fa_icon("fa fa-server") is True

    def test_custom_image_path(self) -> None:
        assert is_fa_icon("img/icon.png") is False

    def test_empty_string(self) -> None:
        assert is_fa_icon("") is False

    def test_non_string(self) -> None:
        assert is_fa_icon(None) is False  # type: ignore


class TestIconToSvg:
    def test_fas_eye(self) -> None:
        svg = icon_to_svg("fas fa-eye")
        assert '<svg class="icon-svg"' in svg
        assert "viewBox" in svg
        assert "path d=" in svg

    def test_fallback_to_link(self) -> None:
        svg = icon_to_svg("fas fa-unknown-icon")
        assert "link" in svg or '<path d="' in svg

    def test_empty_input(self) -> None:
        svg = icon_to_svg("")
        assert svg != ""

    def test_custom_css_class(self) -> None:
        svg = icon_to_svg("fas fa-eye", "custom-icon")
        assert 'class="custom-icon"' in svg

    def test_simple_fa_format(self) -> None:
        svg = icon_to_svg("fa-eye")
        assert "viewBox" in svg


class TestCleanHtmlContent:
    def test_remove_tags(self) -> None:
        assert clean_html_content("<p>Hello</p>") == "Hello"

    def test_escape_entities(self) -> None:
        result = clean_html_content("<script>alert('xss')</script>")
        # 标签被移除后只剩 alert('xss')，然后 ' 被转义为 &#x27;
        assert "alert" in result
        assert "&#x27;" in result
        assert "&lt;" not in result

    def test_empty_string(self) -> None:
        assert clean_html_content("") == ""

    def test_no_html(self) -> None:
        assert clean_html_content("plain text") == "plain text"

    def test_nested_tags(self) -> None:
        assert clean_html_content("<div><span>text</span></div>") == "text"


class TestTruncateText:
    def test_short_text(self) -> None:
        assert truncate_text("hello") == "hello"

    def test_exact_length(self) -> None:
        assert truncate_text("a" * 100) == "a" * 100

    def test_truncate(self) -> None:
        result = truncate_text("a" * 200, 10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_empty_string(self) -> None:
        assert truncate_text("") == ""

    def test_custom_max_length(self) -> None:
        result = truncate_text("hello world", 5)
        assert result == "he..."
