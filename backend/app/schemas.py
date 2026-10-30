"""Schema Pydantic cho request/response, theo contract trong README gốc."""

import re
from typing import Dict, Literal, Union
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app import config

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_HOST_RE = re.compile(r"^[A-Za-z0-9._\-\[\]:]+$")


class UrlValidationError(ValueError):
    """Lỗi kiểm tra URL, mang theo mã lỗi để main.py trả đúng `error`."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def check_url(value: str) -> str:
    """Kiểm tra và chuẩn hóa URL. Ném UrlValidationError nếu không hợp lệ."""
    value = value.strip()
    if not value:
        raise UrlValidationError(config.ERROR_EMPTY_URL, "URL không được để trống.")
    if len(value) > config.MAX_URL_LENGTH:
        raise UrlValidationError(
            config.ERROR_URL_TOO_LONG,
            f"URL vượt quá {config.MAX_URL_LENGTH} ký tự.",
        )
    invalid = "Chuỗi nhập vào không phải định dạng URL hợp lệ."
    if re.search(r"\s", value):
        raise UrlValidationError(config.ERROR_INVALID_URL, invalid)

    # Cho phép URL không có scheme (dataset có dạng này): thêm tạm để phân tích.
    has_scheme = bool(_SCHEME_RE.match(value))
    target = value if has_scheme else "http://" + value
    try:
        parts = urlsplit(target)
        host = parts.hostname
        parts.port  # kiểm tra port hợp lệ (ném ValueError nếu sai)
    except ValueError:
        raise UrlValidationError(config.ERROR_INVALID_URL, invalid)

    if has_scheme and parts.scheme.lower() not in ("http", "https"):
        raise UrlValidationError(config.ERROR_INVALID_URL, invalid)
    if not host or not _HOST_RE.match(host):
        raise UrlValidationError(config.ERROR_INVALID_URL, invalid)
    return value


class PredictRequest(BaseModel):
    """Body của POST /api/v1/predict."""

    url: str = Field(
        ...,
        description="URL cần kiểm tra (có hoặc không có http/https).",
        examples=["http://paypal.com.account-update.fake-domain.com/login"],
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return check_url(value)


class PredictResponse(BaseModel):
    url: str
    prediction: Literal["phishing", "legitimate"]
    is_phishing: bool
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Xác suất của lớp phishing, từ 0 đến 1."
    )
    details: Dict[str, Union[bool, int, float, str]] = Field(
        default_factory=dict,
        description="Dấu hiệu trích xuất từ URL. Khóa phải khớp với Frontend.",
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "url": "http://paypal.com.account-update.fake-domain.com/login",
            "prediction": "phishing",
            "is_phishing": True,
            "confidence": 0.96,
            "details": {
                "has_ip": False,
                "long_url": True,
                "has_at_symbol": False,
                "subdomain_count": 3,
                "has_prefix_suffix": True,
            },
        }
    })


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
    model_loaded: bool
    mock_mode: bool


class ErrorResponse(BaseModel):
    error: Literal["INVALID_URL", "EMPTY_URL", "URL_TOO_LONG", "MODEL_NOT_LOADED"]
    message: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "error": "INVALID_URL",
            "message": "Chuỗi nhập vào không phải định dạng URL hợp lệ.",
        }
    })
