"""
验证函数单元测试
"""

from app.core.validators import (
    format_error_message,
    sanitize_filename,
    validate_category_name,
    validate_form_data,
    validate_icon_path,
    validate_image_filename,
    validate_title,
    validate_url,
)


class TestValidateUrl:
    def test_valid_https(self) -> None:
        assert validate_url("https://example.com") is True

    def test_valid_http(self) -> None:
        assert validate_url("http://example.com") is True

    def test_valid_with_path(self) -> None:
        assert validate_url("https://example.com/path/to/page?q=1") is True

    def test_empty_string(self) -> None:
        assert validate_url("") is False

    def test_no_scheme(self) -> None:
        assert validate_url("example.com") is False

    def test_only_scheme(self) -> None:
        assert validate_url("https://") is False

    def test_invalid_string(self) -> None:
        assert validate_url("not a url") is False


class TestValidateTitle:
    def test_valid_title(self) -> None:
        assert validate_title("测试标题") is True

    def test_empty_string(self) -> None:
        assert validate_title("") is False

    def test_whitespace_only(self) -> None:
        assert validate_title("   ") is False

    def test_too_long(self) -> None:
        assert validate_title("a" * 101) is False

    def test_dangerous_chars(self) -> None:
        assert validate_title("<script>") is False

    def test_quote_char(self) -> None:
        assert validate_title('test"title') is False

    def test_ampersand(self) -> None:
        assert validate_title("a&b") is False

    def test_valid_with_spaces(self) -> None:
        assert validate_title("  My Title  ") is True

    def test_non_string_input(self) -> None:
        assert validate_title(None) is False  # type: ignore


class TestValidateCategoryName:
    def test_valid_name(self) -> None:
        assert validate_category_name("工作") is True

    def test_empty_string(self) -> None:
        assert validate_category_name("") is False

    def test_too_long(self) -> None:
        assert validate_category_name("a" * 51) is False

    def test_dangerous_chars(self) -> None:
        assert validate_category_name("<cat>") is False

    def test_slash(self) -> None:
        assert validate_category_name("a/b") is False

    def test_backslash(self) -> None:
        assert validate_category_name("a\\b") is False

    def test_valid_with_spaces(self) -> None:
        assert validate_category_name("  常用网站  ") is True


class TestSanitizeFilename:
    def test_clean_filename(self) -> None:
        assert sanitize_filename("photo.jpg") == "photo.jpg"

    def test_remove_path_separator(self) -> None:
        assert sanitize_filename("../../etc/passwd") == ".._.._etc_passwd"

    def test_remove_dangerous_chars(self) -> None:
        assert sanitize_filename('a<b>c:d*e?f"g') == "a_b_c_d_e_f_g"

    def test_empty_string(self) -> None:
        assert sanitize_filename("") == ""

    def test_truncate_long_name(self) -> None:
        long_name = "a" * 300 + ".jpg"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".jpg")


class TestValidateIconPath:
    def test_fas_format(self) -> None:
        assert validate_icon_path("fas fa-eye") is True

    def test_fab_format(self) -> None:
        assert validate_icon_path("fab fa-github") is True

    def test_custom_image(self) -> None:
        assert validate_icon_path("img/icon.png") is True

    def test_invalid_extension(self) -> None:
        assert validate_icon_path("img/file.exe") is False

    def test_empty_string(self) -> None:
        assert validate_icon_path("") is False

    def test_random_string(self) -> None:
        assert validate_icon_path("some/path") is False

    def test_non_string(self) -> None:
        assert validate_icon_path(None) is False  # type: ignore


class TestValidateImageFilename:
    def test_valid_png(self) -> None:
        assert validate_image_filename("icon.png") is True

    def test_valid_svg(self) -> None:
        assert validate_image_filename("icon.svg") is True

    def test_invalid_ext(self) -> None:
        assert validate_image_filename("file.exe") is False

    def test_no_extension(self) -> None:
        assert validate_image_filename("file") is False

    def test_empty_string(self) -> None:
        assert validate_image_filename("") is False

    def test_dangerous_chars(self) -> None:
        assert validate_image_filename("a/b.png") is False


class TestValidateFormData:
    def test_valid_data(self) -> None:
        result = validate_form_data(
            {"title": "Test", "url": "https://example.com"}, ["title", "url"]
        )
        assert result["valid"] is True
        assert result["errors"] == {}

    def test_missing_required_field(self) -> None:
        result = validate_form_data({"title": "Test"}, ["title", "url"])
        assert result["valid"] is False
        assert "url" in result["errors"]

    def test_empty_required_field(self) -> None:
        result = validate_form_data(
            {"title": "", "url": "https://example.com"}, ["title"]
        )
        assert result["valid"] is False

    def test_invalid_title(self) -> None:
        result = validate_form_data(
            {"title": "<script>", "url": "https://example.com"}, ["title", "url"]
        )
        assert result["valid"] is False

    def test_invalid_url(self) -> None:
        result = validate_form_data({"title": "Test", "url": "not-a-url"}, ["title", "url"])
        assert result["valid"] is False

    def test_invalid_category(self) -> None:
        result = validate_form_data({"category": "a/b"}, ["category"])
        assert result["valid"] is False

    def test_mixed_errors(self) -> None:
        result = validate_form_data({}, ["title", "url"])
        assert result["valid"] is False
        assert len(result["errors"]) == 2


class TestFormatErrorMessage:
    def test_no_errors(self) -> None:
        assert format_error_message({}) == ""

    def test_single_error(self) -> None:
        assert format_error_message({"title": "标题无效"}) == "标题无效"

    def test_multiple_errors(self) -> None:
        result = format_error_message({"title": "标题无效", "url": "URL无效"})
        assert "多个错误" in result
        assert "标题无效" in result
        assert "URL无效" in result

    def test_none_input(self) -> None:
        assert format_error_message({}) == ""
