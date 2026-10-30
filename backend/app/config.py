"""Cấu hình chung cho backend.

Mọi đường dẫn đều tính từ thư mục gốc của dự án, không ghi cứng đường dẫn tuyệt đối.
"""

from pathlib import Path

APP_NAME = "Phishing Detection API"
APP_VERSION = "0.1.0"

# backend/app/config.py -> parents[2] là thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# Tuần 2: predictor.py nạp các file này khi khởi động.
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
SCALER_PATH = ARTIFACTS_DIR / "scaler.joblib"  # chỉ có nếu mô hình cuối là SVM
FEATURES_PATH = ARTIFACTS_DIR / "features.json"

# Giới hạn độ dài URL đầu vào (ký tự).
MAX_URL_LENGTH = 2048

# Tuần 1: trả dữ liệu giả. Tuần 2 đổi thành False khi nạp mô hình thật.
MOCK_MODE = True

# Mã lỗi, thống nhất với Frontend (xem README gốc, mục API)
ERROR_EMPTY_URL = "EMPTY_URL"
ERROR_INVALID_URL = "INVALID_URL"
ERROR_URL_TOO_LONG = "URL_TOO_LONG"
ERROR_MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
