"""Logic thuần của Frontend (không phụ thuộc Streamlit) để dễ viết unit test."""
import os
import re

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

# Ngưỡng 3 mức rủi ro. Chỉnh cho khớp với app.py hiện tại nếu đang dùng ngưỡng khác.
LOW_THRESHOLD = 0.4
HIGH_THRESHOLD = 0.7

# Nhãn tiếng Việt cho các khóa trong `details` (gộp thêm khóa đang có trong app.py nếu thiếu).
DETAIL_LABELS = {
    # Khóa đã có trong app.py cũ (giữ để tương thích)
    "long_url": "URL có độ dài lớn",
    "has_at_symbol": "URL chứa ký tự @",
    "subdomain_count": "Số lượng subdomain",
    "has_prefix_suffix": "Hostname chứa dấu gạch ngang",
    "url_length": "Độ dài URL",
    "hostname_length": "Độ dài tên miền",
    "path_length": "Độ dài đường dẫn",
    "num_dots": "Số dấu chấm",
    "num_hyphens": "Số dấu gạch ngang",
    "num_underscores": "Số dấu gạch dưới",
    "num_percent": "Số ký tự %",
    "num_question": "Số dấu ?",
    "num_equals": "Số dấu =",
    "num_at": "Số ký tự @",
    "num_digits": "Số chữ số",
    "digit_ratio": "Tỉ lệ chữ số",
    "has_ip": "Hostname sử dụng địa chỉ IP",
    "num_subdomains": "Số tên miền con",
    "hyphen_in_host": "Có dấu gạch ngang trong tên miền",
    "suspicious_tld": "Đuôi tên miền đáng ngờ",
    "host_entropy": "Độ ngẫu nhiên của tên miền",
    "has_https": "Dùng HTTPS",
    "at_count": "Số ký tự @",
    "non_standard_port": "Dùng cổng không chuẩn",
    "sensitive_keywords": "Số từ khóa nhạy cảm",
    "double_slash_in_path": "Có // sau vị trí đầu",
    "path_depth": "Độ sâu đường dẫn",
    "executable_extension": "Đuôi file thực thi (.exe, .php)",
}

RISK_LABELS = {"low": "Rủi ro thấp", "medium": "Rủi ro trung bình", "high": "Rủi ro cao"}

ERROR_MESSAGES = {
    "INVALID_URL": "URL không hợp lệ. Hãy nhập địa chỉ đầy đủ, ví dụ https://example.com.",
    "MODEL_NOT_LOADED": "Mô hình chưa được nạp trên máy chủ. Vui lòng thử lại sau hoặc báo cho nhóm Backend.",
    "TIMEOUT": "Máy chủ phản hồi quá chậm. Vui lòng thử lại.",
    "CONNECTION": "Không kết nối được tới Backend. Hãy kiểm tra Backend đã chạy chưa.",
    "UNKNOWN": "Có lỗi không xác định xảy ra. Vui lòng thử lại.",
}


def get_backend_url() -> str:
    """Đọc địa chỉ Backend từ biến môi trường BACKEND_URL."""
    return os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).strip().rstrip("/")


def check_url_format(url: str):
    """Kiểm tra sơ bộ trước khi gọi API. Trả về (hợp_lệ, thông_báo_lỗi)."""
    url = (url or "").strip()
    if not url:
        return False, "Vui lòng nhập URL."
    if re.search(r"\s", url):
        return False, "URL không được chứa khoảng trắng."
    if not re.match(r"^https?://[^/\s]+", url, flags=re.IGNORECASE):
        return False, "URL phải bắt đầu bằng http:// hoặc https://."
    return True, ""


def risk_level(confidence: float) -> str:
    """Phân mức rủi ro từ confidence (0..1): 'low' | 'medium' | 'high'."""
    c = max(0.0, min(1.0, float(confidence)))
    if c < LOW_THRESHOLD:
        return "low"
    if c < HIGH_THRESHOLD:
        return "medium"
    return "high"


def prettify_key(key: str) -> str:
    """Khóa chưa khai báo: 'some_new_key' -> 'Some new key'."""
    text = str(key).replace("_", " ").strip()
    return text[:1].upper() + text[1:]


def detail_label(key: str) -> str:
    return DETAIL_LABELS.get(key) or prettify_key(key)


def format_detail_value(value) -> str:
    if isinstance(value, bool):
        return "Có" if value else "Không"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def friendly_error(status_code=None, error_code=None, message=None, exc_kind=None) -> str:
    """Chuyển lỗi HTTP / ngoại lệ thành thông báo tiếng Việt.

    exc_kind: 'timeout' hoặc 'connection' khi requests ném ngoại lệ.
    message: nội dung `message` Backend trả về (nếu có).
    """
    if exc_kind == "timeout":
        return ERROR_MESSAGES["TIMEOUT"]
    if exc_kind == "connection":
        return ERROR_MESSAGES["CONNECTION"]
    if status_code == 422 or error_code == "INVALID_URL":
        return f"URL không hợp lệ: {message}" if message else ERROR_MESSAGES["INVALID_URL"]
    if status_code == 503 or error_code == "MODEL_NOT_LOADED":
        if error_code == "MODEL_NOT_LOADED" or not message:
            return ERROR_MESSAGES["MODEL_NOT_LOADED"]
        return message
    return message or ERROR_MESSAGES["UNKNOWN"]

