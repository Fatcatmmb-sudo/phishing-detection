from app.predictor import predict_mock


def test_mock_flags_sensitive_keywords():
    r = predict_mock("http://secure-login.example.com/verify")
    assert r["is_phishing"] is True
    assert r["prediction"] == "phishing"
    assert r["details"]["has_prefix_suffix"] is True


def test_mock_flags_ip_host():
    r = predict_mock("http://192.168.1.1/index")
    assert r["is_phishing"] is True
    assert r["details"]["has_ip"] is True


def test_mock_flags_at_symbol():
    r = predict_mock("http://example.com@evil.com/")
    assert r["details"]["has_at_symbol"] is True
    assert r["is_phishing"] is True


def test_mock_legitimate_url():
    r = predict_mock("https://www.wikipedia.org/")
    assert r["is_phishing"] is False
    assert r["prediction"] == "legitimate"
    assert 0.0 <= r["confidence"] <= 1.0


def test_mock_subdomain_count():
    assert predict_mock("http://a.b.c.example.com/")["details"]["subdomain_count"] == 3
    assert predict_mock("http://example.com/")["details"]["subdomain_count"] == 0
