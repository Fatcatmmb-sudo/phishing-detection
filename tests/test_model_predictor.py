import json

import pytest
from artifact_helpers import (
    FEATURES,
    LEGIT_URL,
    PHISHING_URL,
    fake_extract,
    make_artifacts,
)

from app import config
from app.predictor import ModelNotLoadedError, Predictor, normalize_url


def build(tmp_path, extractor=fake_extract, **kwargs):
    paths = make_artifacts(tmp_path, **kwargs)
    return Predictor(extractor=extractor, **paths)


def test_load_and_predict_phishing(tmp_path):
    p = build(tmp_path)
    assert p.load() is True and p.loaded
    r = p.predict(PHISHING_URL)
    assert set(r) == {"url", "prediction", "is_phishing", "confidence", "details"}
    assert r["url"] == PHISHING_URL
    assert r["prediction"] == "phishing"
    assert r["is_phishing"] is True
    assert 0.5 <= r["confidence"] <= 1.0
    assert list(r["details"]) == FEATURES  # đúng thứ tự features.json


def test_predict_legitimate(tmp_path):
    p = build(tmp_path)
    p.load()
    r = p.predict(LEGIT_URL)
    assert r["is_phishing"] is False
    assert r["prediction"] == "legitimate"
    assert r["confidence"] < 0.5


def test_details_types(tmp_path):
    p = build(tmp_path)
    p.load()
    d = p.predict(PHISHING_URL)["details"]
    assert d["has_https"] is False  # khóa has_* hiển thị dạng bool
    assert d["at_count"] == 1 and type(d["at_count"]) is int
    assert type(d["url_length"]) is int


def test_missing_model_file(tmp_path):
    p = build(tmp_path)
    p.model_path.unlink()
    assert p.load() is False and not p.loaded
    assert "model.joblib" in p.error
    with pytest.raises(ModelNotLoadedError):
        p.predict(PHISHING_URL)


def test_missing_features_file(tmp_path):
    p = build(tmp_path)
    p.features_path.unlink()
    assert p.load() is False
    assert "features.json" in p.error


def test_predict_before_load_raises(tmp_path):
    p = build(tmp_path)
    with pytest.raises(ModelNotLoadedError):
        p.predict(PHISHING_URL)


def test_feature_order_mismatch_is_rejected(tmp_path):
    p = build(tmp_path, features=list(reversed(FEATURES)))
    assert p.load() is False
    assert "không khớp" in p.error


def test_wrong_feature_count_is_rejected(tmp_path):
    p = build(tmp_path, features=FEATURES + ["extra"])
    assert p.load() is False


def test_extractor_missing_a_feature_is_rejected(tmp_path):
    def partial(url):
        return {k: v for k, v in fake_extract(url).items() if k != "at_count"}

    p = build(tmp_path, extractor=partial)
    assert p.load() is False
    assert "at_count" in p.error


def test_extractor_not_implemented(tmp_path, monkeypatch):
    monkeypatch.setattr("app.feature_extractor.extract", None, raising=False)
    p = build(tmp_path, extractor=None)
    assert p.load() is False
    assert "chưa được cài đặt" in p.error


def test_features_json_accepts_object_form(tmp_path):
    p = build(tmp_path)
    p.features_path.write_text(json.dumps({"features": FEATURES}), encoding="utf-8")
    assert p.load() is True


@pytest.mark.parametrize("content", ["[]", '"abc"', "[1, 2]", '["a", "a"]', "not json"])
def test_bad_features_json_is_rejected(tmp_path, content):
    p = build(tmp_path)
    p.features_path.write_text(content, encoding="utf-8")
    assert p.load() is False


def test_integer_labels(tmp_path):
    p = build(tmp_path, labels=(0, 1))  # README: 1 = phishing
    assert p.load() is True
    assert p.predict(PHISHING_URL)["is_phishing"] is True
    assert p.predict(LEGIT_URL)["is_phishing"] is False


def test_phishing_class_not_in_second_column(tmp_path):
    # classes_ sắp theo thứ tự chữ cái: ["phishing", "safe"] -> phishing là cột 0
    p = build(tmp_path, labels=("safe", "phishing"))
    assert p.load() is True
    assert p.phishing_index == 0
    r = p.predict(PHISHING_URL)
    assert r["is_phishing"] is True and r["confidence"] >= 0.5
    assert p.predict(LEGIT_URL)["confidence"] < 0.5


def test_no_phishing_class_is_rejected(tmp_path):
    p = build(tmp_path, labels=("cat", "dog"))
    assert p.load() is False
    assert "phishing" in p.error


def test_with_scaler(tmp_path):
    p = build(tmp_path, scaler=True)
    assert p.load() is True and p.scaler is not None
    assert p.predict(PHISHING_URL)["is_phishing"] is True
    assert p.predict(LEGIT_URL)["is_phishing"] is False


def test_extractor_receives_normalized_url(tmp_path):
    seen = []

    def spy(url):
        seen.append(url)
        return fake_extract(url)

    p = build(tmp_path, extractor=spy)
    p.load()
    r = p.predict("  http://exa[.]mple.com/@  ")
    assert seen[-1] == "http://exa.mple.com/@"
    assert r["url"] == "  http://exa[.]mple.com/@  "  # trả lại đúng chuỗi được truyền vào


def test_normalize_url():
    assert normalize_url("  http://a[.]b[.]c/  ") == "http://a.b.c/"


def test_default_paths_come_from_config(tmp_path, monkeypatch):
    paths = make_artifacts(tmp_path)
    monkeypatch.setattr(config, "MODEL_PATH", paths["model_path"])
    monkeypatch.setattr(config, "FEATURES_PATH", paths["features_path"])
    monkeypatch.setattr(config, "SCALER_PATH", paths["scaler_path"])
    p = Predictor(extractor=fake_extract)
    assert p.load() is True


def test_threshold_is_respected(tmp_path, monkeypatch):
    p = build(tmp_path, scaler=True)
    p.load()
    monkeypatch.setattr(config, "PHISHING_THRESHOLD", 1.01)
    assert p.predict(PHISHING_URL)["is_phishing"] is False
