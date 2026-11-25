"""Test API ở chế độ mô hình thật (MOCK_MODE=False): 503, health, kết quả dự đoán."""

import pytest
from artifact_helpers import LEGIT_URL, PHISHING_URL, fake_extract, make_artifacts
from fastapi.testclient import TestClient

from app import config
from app import predictor as predictor_module
from app.main import app
from app.predictor import Predictor


@pytest.fixture
def client(monkeypatch):
    # Không dùng `with TestClient(...)` nên lifespan không chạy; test tự gắn predictor.
    monkeypatch.setattr(config, "MOCK_MODE", False)
    return TestClient(app)


@pytest.fixture
def loaded_predictor(tmp_path, monkeypatch):
    p = Predictor(extractor=fake_extract, **make_artifacts(tmp_path))
    assert p.load()
    monkeypatch.setattr(predictor_module, "_predictor", p)
    return p


@pytest.fixture
def unloaded_predictor(tmp_path, monkeypatch):
    p = Predictor(
        model_path=tmp_path / "model.joblib",
        features_path=tmp_path / "features.json",
        scaler_path=tmp_path / "scaler.joblib",
        extractor=fake_extract,
    )
    assert p.load() is False
    monkeypatch.setattr(predictor_module, "_predictor", p)
    return p


def test_predict_returns_503_when_model_not_loaded(client, unloaded_predictor):
    r = client.post("/api/v1/predict", json={"url": "https://www.wikipedia.org/"})
    assert r.status_code == 503
    body = r.json()
    assert body["error"] == "MODEL_NOT_LOADED"
    assert set(body) == {"error", "message"}


def test_health_when_model_not_loaded(client, unloaded_predictor):
    body = client.get("/health").json()
    assert body["model_loaded"] is False
    assert body["mock_mode"] is False


def test_health_when_model_loaded(client, loaded_predictor):
    body = client.get("/health").json()
    assert body["model_loaded"] is True
    assert body["mock_mode"] is False


def test_predict_phishing_with_real_model(client, loaded_predictor):
    r = client.post("/api/v1/predict", json={"url": PHISHING_URL})
    assert r.status_code == 200
    body = r.json()
    assert body["is_phishing"] is True
    assert body["prediction"] == "phishing"
    assert 0.5 <= body["confidence"] <= 1.0
    assert set(body["details"]) == {"url_length", "has_https", "at_count"}


def test_predict_legitimate_with_real_model(client, loaded_predictor):
    body = client.post("/api/v1/predict", json={"url": LEGIT_URL}).json()
    assert body["is_phishing"] is False
    assert body["prediction"] == "legitimate"


def test_invalid_url_still_422_without_model(client, unloaded_predictor):
    # Kiểm tra URL chạy trước khi đụng tới mô hình.
    r = client.post("/api/v1/predict", json={"url": ""})
    assert r.status_code == 422
    assert r.json()["error"] == "EMPTY_URL"
