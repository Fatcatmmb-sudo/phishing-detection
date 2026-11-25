import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "frontend"))
import logic  # noqa: E402


# ---- BACKEND_URL ----
def test_backend_url_default(monkeypatch):
    monkeypatch.delenv("BACKEND_URL", raising=False)
    assert logic.get_backend_url() == "http://127.0.0.1:8000"


def test_backend_url_from_env_strips_slash(monkeypatch):
    monkeypatch.setenv("BACKEND_URL", "http://10.0.0.5:9000/")
    assert logic.get_backend_url() == "http://10.0.0.5:9000"


# ---- kiểm tra định dạng URL ----
@pytest.mark.parametrize("url", ["https://example.com", "http://a.b/c?d=1", "HTTPS://Example.com"])
def test_url_valid(url):
    assert logic.check_url_format(url) == (True, "")


@pytest.mark.parametrize("url", ["", "   ", None, "example.com", "ftp://x.com", "http://", "https://a b.com"])
def test_url_invalid(url):
    ok, msg = logic.check_url_format(url)
    assert ok is False and msg


# ---- mức rủi ro ----
@pytest.mark.parametrize(
    "c,expected",
    [(0.0, "low"), (0.39, "low"), (0.4, "medium"), (0.69, "medium"), (0.7, "high"), (1.0, "high"),
     (-0.5, "low"), (1.7, "high")],
)
def test_risk_level(c, expected):
    assert logic.risk_level(c) == expected


# ---- nhãn details ----
def test_known_label():
    assert logic.detail_label("has_https") == "Dùng HTTPS"


def test_unknown_label_is_prettified():
    assert logic.detail_label("some_new_key") == "Some new key"


def test_format_detail_value():
    assert logic.format_detail_value(True) == "Có"
    assert logic.format_detail_value(False) == "Không"
    assert logic.format_detail_value(0.5) == "0.5"
    assert logic.format_detail_value(3) == "3"


# ---- thông báo lỗi ----
def test_error_422_with_message():
    assert logic.friendly_error(422, "INVALID_URL", "URL rỗng") == "URL không hợp lệ: URL rỗng"


def test_error_422_without_message():
    assert logic.friendly_error(422) == logic.ERROR_MESSAGES["INVALID_URL"]


def test_error_model_not_loaded():
    assert logic.friendly_error(503, "MODEL_NOT_LOADED", "x") == logic.ERROR_MESSAGES["MODEL_NOT_LOADED"]
    assert logic.friendly_error(503) == logic.ERROR_MESSAGES["MODEL_NOT_LOADED"]


def test_error_503_other_uses_backend_message():
    assert logic.friendly_error(503, "OTHER", "Bảo trì") == "Bảo trì"


def test_error_timeout_and_connection():
    assert logic.friendly_error(exc_kind="timeout") == logic.ERROR_MESSAGES["TIMEOUT"]
    assert logic.friendly_error(exc_kind="connection") == logic.ERROR_MESSAGES["CONNECTION"]


def test_error_unknown():
    assert logic.friendly_error(500) == logic.ERROR_MESSAGES["UNKNOWN"]
    assert logic.friendly_error(500, None, "Lỗi nội bộ") == "Lỗi nội bộ"


def test_at_count_label():
    assert logic.detail_label("at_count") == "Số ký tự @"