"""Điểm vào của FastAPI.

Chạy (từ thư mục gốc dự án):
    cd backend
    uvicorn app.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app import config
from app.predictor import predict_mock
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
    UrlValidationError,
)

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="API phát hiện website phishing từ URL (đồ án Máy học).",
)

# Cho phép Frontend (Streamlit chạy cổng khác) gọi API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Mọi lỗi đầu vào -> 422 với {"error": <mã>, "message": <thông báo>}."""
    code = config.ERROR_INVALID_URL
    message = "Chuỗi nhập vào không phải định dạng URL hợp lệ."
    for err in exc.errors():
        original = (err.get("ctx") or {}).get("error")
        if isinstance(original, UrlValidationError):
            code, message = original.code, original.message
            break
        if err.get("type") == "missing":
            message = "Thiếu trường 'url' trong body."
            break
    return JSONResponse(status_code=422, content={"error": code, "message": message})


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Kiểm tra trạng thái dịch vụ. Tuần 1 chưa nạp mô hình nên model_loaded=False."""
    return HealthResponse(
        version=config.APP_VERSION,
        model_loaded=False,
        mock_mode=config.MOCK_MODE,
    )


@app.post(
    "/api/v1/predict",
    response_model=PredictResponse,
    responses={
        422: {"model": ErrorResponse, "description": "URL rỗng, sai định dạng hoặc quá dài"},
        503: {"model": ErrorResponse, "description": "Chưa nạp được mô hình (MODEL_NOT_LOADED)"},
    },
    tags=["predict"],
)
def predict(request: PredictRequest) -> PredictResponse:
    """Dự đoán một URL. Tuần 1: trả dữ liệu giả đúng format contract."""
    return PredictResponse(**predict_mock(request.url))
