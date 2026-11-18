"""Tạo artifacts giả (mô hình sklearn thật, rất nhỏ) trong thư mục tạm cho test.

Không phụ thuộc file của ML: bộ đặc trưng và hàm extract dưới đây chỉ dùng trong test.
"""

import json

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

FEATURES = ["url_length", "has_https", "at_count"]

LEGIT = [
    "https://www.wikipedia.org",
    "https://www.google.com",
    "https://github.com/user/repo",
    "https://example.com/index.html",
    "https://www.python.org/downloads",
]
PHISH = [
    "http://paypal.com@evil.example.net/login",
    "http://a@b.example.org/x/y/z",
    "http://login@secure-bank.example/update",
    "http://support@verify-account.example/home",
    "http://x@y.example.io/free-gift",
]

PHISHING_URL = "http://secure@evil.example.net/login"
LEGIT_URL = "https://www.wikipedia.org/wiki/Python"


def fake_extract(url):
    return {
        "url_length": len(url),
        "has_https": int(url.lower().startswith("https://")),
        "at_count": url.count("@"),
    }


def make_artifacts(tmp_path, labels=("legitimate", "phishing"), scaler=False, features=None):
    """Huấn luyện mô hình nhỏ và lưu model.joblib, features.json (và scaler.joblib)."""
    urls = LEGIT + PHISH
    X = pd.DataFrame([fake_extract(u) for u in urls], columns=FEATURES)
    y = [labels[0]] * len(LEGIT) + [labels[1]] * len(PHISH)

    paths = {
        "model_path": tmp_path / "model.joblib",
        "features_path": tmp_path / "features.json",
        "scaler_path": tmp_path / "scaler.joblib",
    }
    if scaler:
        sc = StandardScaler().fit(X)
        model = LogisticRegression(max_iter=1000).fit(sc.transform(X), y)
        joblib.dump(sc, paths["scaler_path"])
    else:
        model = DecisionTreeClassifier(random_state=42).fit(X, y)
    joblib.dump(model, paths["model_path"])
    paths["features_path"].write_text(
        json.dumps(features if features is not None else FEATURES), encoding="utf-8"
    )
    return paths
