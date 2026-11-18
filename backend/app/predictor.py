"""Bộ dự đoán.

- `Predictor`: nạp artifacts (model.joblib, features.json, scaler.joblib nếu có) khi
  khởi động, rồi dự đoán theo luồng: chuẩn hóa URL -> feature_extractor.extract(url)
  -> sắp xếp theo features.json -> (scaler) -> predict_proba -> kết quả theo contract.
  Thiếu hoặc lỗi artifact thì `loaded=False` và `predict()` ném ModelNotLoadedError
  (main.py đổi thành 503 MODEL_NOT_LOADED).
- `predict_mock`: dữ liệu giả của Tuần 1, bật bằng biến môi trường PHISHING_MOCK=1
  để Frontend phát triển khi chưa có mô hình.
"""

import json
import logging
import re
from pathlib import Path
from typing import Callable, List, Mapping, Optional
from urllib.parse import urlsplit

from app import config

log = logging.getLogger("predictor")

# URL dùng để thử hàm extract() lúc nạp, kiểm tra nó trả đủ các đặc trưng.
_PROBE_URL = "http://example.com/"

# Các giá trị nhãn được coi là lớp phishing (README: 1 = phishing; notebook dùng chuỗi).
_PHISHING_LABELS = {1, "1", "phishing"}


class ModelNotLoadedError(RuntimeError):
    """Mô hình hoặc artifact chưa sẵn sàng."""


def normalize_url(url: str) -> str:
    """Chuẩn hóa giống bước tiền xử lý của ML (scripts/preprocess_dataset.py)."""
    return str(url).strip().replace("[.]", ".")


class Predictor:
    def __init__(
        self,
        model_path: Optional[Path] = None,
        features_path: Optional[Path] = None,
        scaler_path: Optional[Path] = None,
        extractor: Optional[Callable[[str], Mapping]] = None,
    ):
        # Đọc đường dẫn lúc tạo đối tượng (không lúc import) để test đổi được config.
        self.model_path = Path(model_path or config.MODEL_PATH)
        self.features_path = Path(features_path or config.FEATURES_PATH)
        self.scaler_path = Path(scaler_path or config.SCALER_PATH)
        self._extractor = extractor

        self.model = None
        self.scaler = None
        self.features: List[str] = []
        self.phishing_index = 0
        self.error: Optional[str] = None

    @property
    def loaded(self) -> bool:
        return self.model is not None

    # ------------------------------------------------------------------ nạp
    def load(self) -> bool:
        """Nạp artifacts. Trả True nếu sẵn sàng; nếu không thì ghi lý do vào self.error."""
        self.model = self.scaler = None
        self.error = None
        try:
            self._load()
        except Exception as exc:  # mọi lỗi nạp đều dẫn tới MODEL_NOT_LOADED
            self.model = self.scaler = None
            self.error = f"{type(exc).__name__}: {exc}"
            log.error("Không nạp được mô hình: %s", self.error)
            return False
        log.info("Đã nạp mô hình (%d đặc trưng).", len(self.features))
        return True

    def _load(self) -> None:
        import joblib

        for path in (self.model_path, self.features_path):
            if not path.exists():
                raise FileNotFoundError(f"Thiếu file {path.name} trong {path.parent}")

        features = self._read_features()
        extractor = self._resolve_extractor()
        model = joblib.load(self.model_path)
        scaler = joblib.load(self.scaler_path) if self.scaler_path.exists() else None

        phishing_index = self._find_phishing_index(model)
        self._check_names(model, features, "mô hình")
        if scaler is not None:
            self._check_names(scaler, features, "scaler")
        self._check_extractor(extractor, features)

        self.features = features
        self._extractor = extractor
        self.model = model
        self.scaler = scaler
        self.phishing_index = phishing_index

    def _read_features(self) -> List[str]:
        data = json.loads(self.features_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("features")
        if not isinstance(data, list) or not data or not all(isinstance(f, str) for f in data):
            raise ValueError("features.json phải là danh sách tên đặc trưng (không rỗng).")
        if len(set(data)) != len(data):
            raise ValueError("features.json có tên đặc trưng trùng nhau.")
        return data

    def _resolve_extractor(self) -> Callable[[str], Mapping]:
        if self._extractor is not None:
            return self._extractor
        from app import feature_extractor

        fn = getattr(feature_extractor, "extract", None)
        if not callable(fn):
            raise ImportError("feature_extractor.extract(url) chưa được cài đặt.")
        return fn

    @staticmethod
    def _find_phishing_index(model) -> int:
        """Tìm cột xác suất của lớp phishing theo model.classes_ (không giả định vị trí)."""
        classes = getattr(model, "classes_", None)
        if classes is None:
            raise ValueError("Mô hình không có thuộc tính classes_.")
        for i, label in enumerate(classes):
            key = label.item() if hasattr(label, "item") else label
            if isinstance(key, str):
                key = key.strip().lower()
            if key in _PHISHING_LABELS:
                return i
        raise ValueError(f"Không tìm thấy lớp phishing trong classes_={list(classes)}.")

    @staticmethod
    def _check_names(obj, features: List[str], what: str) -> None:
        """Chặn lỗi sai thứ tự cột: so features.json với tên cột lúc huấn luyện."""
        names = getattr(obj, "feature_names_in_", None)
        if names is not None and list(names) != features:
            raise ValueError(
                f"features.json không khớp với {what}: "
                f"features.json={features}, lúc huấn luyện={list(names)}."
            )
        n = getattr(obj, "n_features_in_", None)
        if n is not None and n != len(features):
            raise ValueError(f"{what} cần {n} đặc trưng nhưng features.json có {len(features)}.")

    @staticmethod
    def _check_extractor(extractor, features: List[str]) -> None:
        raw = extractor(_PROBE_URL)
        if not isinstance(raw, Mapping):
            raise TypeError("extract(url) phải trả về dict {tên đặc trưng: giá trị}.")
        missing = [f for f in features if f not in raw]
        if missing:
            raise ValueError(f"extract() thiếu đặc trưng có trong features.json: {missing}")

    # ------------------------------------------------------------ dự đoán
    def predict(self, url: str) -> dict:
        if not self.loaded:
            raise ModelNotLoadedError(self.error or "Mô hình chưa được nạp.")
        import pandas as pd

        raw = self._extractor(normalize_url(url))
        values = [_plain(raw[f]) for f in self.features]
        X = pd.DataFrame([values], columns=self.features)
        if self.scaler is not None:
            X = self.scaler.transform(X)

        confidence = float(self.model.predict_proba(X)[0][self.phishing_index])
        confidence = min(max(confidence, 0.0), 1.0)
        is_phishing = confidence >= config.PHISHING_THRESHOLD

        return {
            "url": url,
            "prediction": "phishing" if is_phishing else "legitimate",
            "is_phishing": is_phishing,
            "confidence": confidence,
            "details": {f: _display(f, raw[f]) for f in self.features},
        }


def _plain(value):
    """numpy -> kiểu Python; bool -> int để vector đặc trưng toàn số."""
    value = value.item() if hasattr(value, "item") else value
    return int(value) if isinstance(value, bool) else value


def _display(name: str, value):
    """Giá trị hiển thị trong `details`: cờ has_/is_ thành bool, số thực làm tròn."""
    value = value.item() if hasattr(value, "item") else value
    if name.startswith(("has_", "is_")) and value in (0, 1):
        return bool(value)
    if isinstance(value, float):
        return round(value, 4)
    return value


_predictor: Optional[Predictor] = None


def get_predictor() -> Predictor:
    """Đối tượng Predictor dùng chung. Chưa nạp cho tới khi gọi .load()."""
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor


# ---------------------------------------------------------------- dữ liệu giả
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
