"""
工具函数单元测试
"""

import re
from pathlib import Path

from app.utils import (
    _ICON_SVG_MAP,
    THUMBNAIL_SIZE,
    clean_html_content,
    generate_thumbnail,
    get_version,
    icon_to_svg,
    is_fa_icon,
    thumbnail_path,
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

    def test_svg_has_correct_css_class(self) -> None:
        svg = icon_to_svg("fas fa-link")
        assert 'class="icon-svg"' in svg

    def test_svg_contains_viewbox_and_path(self) -> None:
        svg = icon_to_svg("fas fa-plus")
        assert 'viewBox="0 0 448 512"' in svg
        assert "<path d=" in svg

    def test_svg_no_invalid_html(self) -> None:
        svg = icon_to_svg("fas fa-eye")
        assert "<script" not in svg
        assert "onload" not in svg


class TestIconSizingCSS:
    """验证 CSS 文件中图标尺寸配置一致"""

    CSS_PATH = "app/static/css/style.css"

    def test_nav_item_icon_container_size(self) -> None:
        """SVG 图标容器宽度应为 64px"""
        with open(self.CSS_PATH) as f:
            css = f.read()
        assert ".nav-item .nav-item-icon" in css
        assert "width: 64px" in css
        assert "height: 64px" in css
        assert "box-sizing: border-box" in css

    def test_nav_item_svg_icon_size(self) -> None:
        """SVG 图标本身应为 40x40px"""
        with open(self.CSS_PATH) as f:
            css = f.read()
        assert ".nav-item .nav-item-icon .icon-svg" in css
        assert "width: 40px" in css
        assert "height: 40px" in css

    def test_icon_img_uses_border_box(self) -> None:
        """自定义图片图标应使用 box-sizing: border-box"""
        with open(self.CSS_PATH) as f:
            css = f.read()
        assert ".icon-img" in css
        assert "box-sizing: border-box" in css

    def test_no_border_on_icon_container(self) -> None:
        """SVG 图标容器无边框"""
        with open(self.CSS_PATH) as f:
            css = f.read()
        idx = css.index(".nav-item i,\n.nav-item .nav-item-icon")
        block_end = css.index("}", idx)
        block = css[idx:block_end]
        assert "border:" not in block


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


class TestIconSvgConsistency:
    """验证 Python 和 JS 中的 SVG 图标映射一致"""

    JS_PATH = "app/static/js/script.js"

    def test_icon_keys_match_js(self) -> None:
        with open(self.JS_PATH) as f:
            js_content = f.read()

        m = re.search(r"var ICON_SVG_MAP\s*=\s*\{(.*?)\};", js_content, re.DOTALL)
        assert m, "未能在 JS 中找到 ICON_SVG_MAP"
        map_block = m.group(1)
        js_keys = set(re.findall(r"(?:'|\b)([\w-]+)(?:'|\s*)\s*:", map_block))
        py_keys = set(_ICON_SVG_MAP.keys())

        common = js_keys & py_keys
        only_js = js_keys - py_keys
        only_py = py_keys - js_keys

        assert common, "Python 与 JS 的 SVG 图标映射没有共同的键"
        assert not only_js, f"JS 中多出的图标键: {only_js}"
        assert not only_py, f"Python 中多出的图标键: {only_py}"


class TestGenerateThumbnail:
    def test_thumbnail_created(self, tmp_path: Path) -> None:
        from PIL import Image
        src = str(tmp_path / "test.png")
        img = Image.new("RGB", (200, 300), color="red")
        img.save(src)
        thumb_dir = str(tmp_path / "thumbs")
        result = generate_thumbnail(src, thumb_dir)
        assert result is not None
        thumb = Image.open(result)
        assert thumb.width <= THUMBNAIL_SIZE
        assert thumb.height <= THUMBNAIL_SIZE

    def test_thumbnail_invalid_image(self, tmp_path: Path) -> None:
        src = str(tmp_path / "not_an_image.txt")
        with open(src, "w") as f:
            f.write("not an image")
        result = generate_thumbnail(src, str(tmp_path / "thumbs"))
        assert result is None

    def test_thumbnail_svg_skipped(self, tmp_path: Path) -> None:
        src = str(tmp_path / "icon.svg")
        with open(src, "w") as f:
            f.write("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
        result = generate_thumbnail(src, str(tmp_path / "thumbs"))
        assert result is None


class TestThumbnailPath:
    def test_custom_image(self) -> None:
        assert thumbnail_path("img/icon.png") == "img/thumbs/icon.png"

    def test_custom_image_subdir(self) -> None:
        assert thumbnail_path("img/sub/dir/file.jpg") == "img/thumbs/sub/dir/file.jpg"

    def test_fa_icon_unchanged(self) -> None:
        assert thumbnail_path("fas fa-eye") == "fas fa-eye"

    def test_empty_string(self) -> None:
        assert thumbnail_path("") == ""

    def test_non_string(self) -> None:
        assert thumbnail_path("fa-link") == "fa-link"

    def test_svg_skipped(self) -> None:
        assert thumbnail_path("img/icon.svg") == "img/icon.svg"

    def test_svg_deep_path_skipped(self) -> None:
        assert thumbnail_path("img/sub/dir/file.svg") == "img/sub/dir/file.svg"
