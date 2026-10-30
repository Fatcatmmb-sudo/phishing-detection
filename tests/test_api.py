import pytest
from fastapi.testclient import TestClient

from app.config import MAX_URL_LENGTH
from app.main import app

client = TestClient(app)


def post(url):
    return client.post("/api/v1/predict", json={"url": url})


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert set(body) >= {"version", "model_loaded", "mock_mode"}


def test_predict_phishing_mock_matches_contract():
    r = post("http://paypal.com.account-update.fake-domain.com/login")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"url", "prediction", "is_phishing", "confidence", "details"}
    assert body["prediction"] == "phishing"
    assert body["is_phishing"] is True
    assert 0.0 <= body["confidence"] <= 1.0
    assert set(body["details"]) >= {
        "has_ip", "long_url", "has_at_symbol", "subdomain_count", "has_prefix_suffix",
    }


def test_predict_legitimate_mock():
    r = post("https://www.wikipedia.org/")
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] == "legitimate"
    assert body["is_phishing"] is False


def test_url_without_scheme_is_accepted():
    assert post("example.com/path").status_code == 200


def test_whitespace_around_url_is_stripped():
    r = post("  https://www.wikipedia.org/  ")
    assert r.status_code == 200
    assert r.json()["url"] == "https://www.wikipedia.org/"


@pytest.mark.parametrize("bad", ["", "   "])
def test_empty_url_returns_422(bad):
    r = post(bad)
    assert r.status_code == 422
    assert r.json()["error"] == "EMPTY_URL"


@pytest.mark.parametrize(
    "bad",
    [
        "http://",                   # thiếu host
        "ht tp://example.com",       # khoảng trắng
        "http://exa mple.com",       # khoảng trắng trong host
        "ftp://example.com",         # giao thức không hỗ trợ
        "httpss://example.com",      # scheme sai (lỗi có trong dataset)
        "http://example.com:99999",  # port không hợp lệ
        "http://@@@",                # host rác
    ],
)
def test_malformed_url_returns_422(bad):
    r = post(bad)
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "INVALID_URL"
    assert body["message"]


def test_too_long_url_returns_422():
    r = post("http://example.com/" + "a" * MAX_URL_LENGTH)
    assert r.status_code == 422
    assert r.json()["error"] == "URL_TOO_LONG"


def test_url_at_max_length_is_accepted():
    prefix = "http://example.com/"
    assert post(prefix + "a" * (MAX_URL_LENGTH - len(prefix))).status_code == 200


def test_missing_url_field_returns_422():
    r = client.post("/api/v1/predict", json={})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_URL"


def test_non_string_url_returns_422():
    r = client.post("/api/v1/predict", json={"url": 123})
    assert r.status_code == 422
    assert r.json()["error"] == "INVALID_URL"


def test_error_body_has_only_error_and_message():
    assert set(post("").json()) == {"error", "message"}


def test_root_redirects_to_docs():
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/docs"
