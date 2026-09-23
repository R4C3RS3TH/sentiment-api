import pytest

from app.preprocessing import InvalidTextError, clean_text, validate_text


def test_clean_text_strips_extra_whitespace():
    assert clean_text("  hola   mundo  ") == "hola mundo"


def test_clean_text_collapses_newlines_and_tabs():
    assert clean_text("hola\n\tmundo") == "hola mundo"


def test_validate_text_accepts_valid_string():
    assert validate_text("me encanta este producto") == "me encanta este producto"


def test_validate_text_rejects_empty_string():
    with pytest.raises(InvalidTextError):
        validate_text("   ")


def test_validate_text_rejects_none():
    with pytest.raises(InvalidTextError):
        validate_text(None)


def test_validate_text_rejects_non_string_input():
    with pytest.raises(InvalidTextError):
        validate_text(12345)


def test_validate_text_rejects_text_too_long():
    with pytest.raises(InvalidTextError):
        validate_text("a" * 1001)
