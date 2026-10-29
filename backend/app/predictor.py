"""Bộ dự đoán.

Tuần 1: chỉ có `predict_mock` trả dữ liệu giả đúng format contract để Frontend gọi thử.
Tuần 2: nạp model.joblib + features.json, dùng feature_extractor.extract(url),
        lấy confidence = predict_proba()[:, 1]; thiếu artifact thì trả MODEL_NOT_LOADED.
"""

import re
from urllib.parse import urlsplit

_KEYWORDS = ("login", "secure", "verify", "account", "update", "bank")
_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_LONG_URL = 75


def _host_of(url: str) -> str:
    target = url if "://" in url else "http://" + url
    return (urlsplit(target).hostname or "").lower()


def predict_mock(url: str) -> dict:
    """Trả kết quả giả nhưng có quy luật, để demo được cả khung đỏ lẫn xanh.

    Có từ khóa nhạy cảm, host là IP, hoặc có '@' -> phishing (0.96).
    Ngược lại -> hợp pháp (0.05). Khóa `details` theo ví dụ trong README gốc.
    """
    lowered = url.lower()
    host = _host_of(url)
    has_ip = bool(_IP_RE.match(host))
    has_at = "@" in url
    keyword_count = sum(lowered.count(k) for k in _KEYWORDS)

    is_phishing = keyword_count > 0 or has_ip or has_at
    return {
        "url": url,
        "prediction": "phishing" if is_phishing else "legitimate",
        "is_phishing": is_phishing,
        "confidence": 0.96 if is_phishing else 0.05,
        "details": {
            "has_ip": has_ip,
            "long_url": len(url) > _LONG_URL,
            "has_at_symbol": has_at,
            "subdomain_count": 0 if has_ip else max(host.count(".") - 1, 0),
            "has_prefix_suffix": "-" in host,
        },
    }
