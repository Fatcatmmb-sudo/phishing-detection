"""Cấu hình chung cho backend.

Mọi đường dẫn đều tính từ thư mục gốc của dự án, không ghi cứng đường dẫn tuyệt đối.
"""

import os
from pathlib import Path

APP_NAME = "Phishing Detection API"
APP_VERSION = "0.1.0"

# backend/app/config.py -> parents[2] là thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# predictor.py nạp các file này khi khởi động.
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
SCALER_PATH = ARTIFACTS_DIR / "scaler.joblib"  # chỉ có nếu mô hình cuối là SVM
FEATURES_PATH = ARTIFACTS_DIR / "features.json"

# Giới hạn độ dài URL đầu vào (ký tự).
MAX_URL_LENGTH = 2048

# Mặc định dùng mô hình thật. Đặt PHISHING_MOCK=1 để trả dữ liệu giả (Frontend dev/demo
# khi chưa có artifacts), ví dụ:  $env:PHISHING_MOCK = "1"  rồi chạy uvicorn.
MOCK_MODE = os.getenv("PHISHING_MOCK", "").strip().lower() in ("1", "true", "yes")

# Ngưỡng xác suất để xếp là phishing.
PHISHING_THRESHOLD = 0.5

# Mã lỗi, thống nhất với Frontend (xem README gốc, mục API)
ERROR_EMPTY_URL = "EMPTY_URL"
ERROR_INVALID_URL = "INVALID_URL"
ERROR_URL_TOO_LONG = "URL_TOO_LONG"
ERROR_MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
