
"""Trích xuất 10 đặc trưng từ một URL."""

from urllib.parse import urlsplit


def extract(url: str) -> dict:
    """
    Nhận một URL và trả về dictionary gồm 10 đặc trưng.

    Các đặc trưng phải đúng tên và thứ tự trong artifacts/features.json.
    """

    # 1. Chuẩn hóa URL giống preprocess_dataset.py
    normalized_url = str(url).strip().replace("[.]", ".")

    # 2. Tách hostname từ URL
    try:
        parsed = urlsplit(normalized_url)
        hostname = (parsed.hostname or "").lower()
    except ValueError as exc:
        raise ValueError("URL không hợp lệ.") from exc

    if not hostname:
        raise ValueError("URL không có hostname hợp lệ.")

    # 3. Trích xuất 10 đặc trưng
    features = {
        # Độ dài toàn bộ URL
        "url_length": len(normalized_url),

        # Độ dài hostname
        "hostname_length": len(hostname),

        # Số dấu chấm trong URL
        "dot_count": normalized_url.count("."),

        # Số dấu gạch ngang
        "hyphen_count": normalized_url.count("-"),

        # Số chữ số
        "digit_count": sum(char.isdigit() for char in normalized_url),

        # Số ký tự @
        "at_count": normalized_url.count("@"),

        # Số dấu /
        "slash_count": normalized_url.count("/"),

        # Số dấu ?
        "question_count": normalized_url.count("?"),

        # Số dấu =
        "equal_count": normalized_url.count("="),

        # Có bắt đầu bằng HTTPS hay không: 1 có, 0 không
        "has_https": int(normalized_url.lower().startswith("https://")),
    }

    return features
