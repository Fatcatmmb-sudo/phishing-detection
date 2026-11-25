"""Điểm vào của FastAPI.

Chạy (từ thư mục gốc dự án):
    cd backend
    uvicorn app.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs

Mặc định nạp mô hình thật từ artifacts/. Đặt biến môi trường PHISHING_MOCK=1
để trả dữ liệu giả (không cần artifacts).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app import config
from app import predictor as predictor_module
from app.predictor import ModelNotLoadedError
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
    UrlValidationError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Nạp mô hình một lần khi khởi động. Nạp lỗi vẫn chạy, /predict trả 503."""
    if not config.MOCK_MODE:
        predictor_module.get_predictor().load()
    yield


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="API phát hiện website phishing từ URL (đồ án Máy học).",
    lifespan=lifespan,
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


@app.exception_handler(ModelNotLoadedError)
async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
    """Chưa nạp được mô hình -> 503 MODEL_NOT_LOADED (lý do chi tiết nằm trong log server)."""
    return JSONResponse(
        status_code=503,
        content={
            "error": config.ERROR_MODEL_NOT_LOADED,
            "message": (
                "Mô hình chưa được nạp. Kiểm tra thư mục artifacts/ "
                "(model.joblib, features.json) và log của server."
            ),
        },
    )


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Trạng thái dịch vụ. model_loaded=True khi đã nạp xong mô hình thật."""
    loaded = (not config.MOCK_MODE) and predictor_module.get_predictor().loaded
    return HealthResponse(
        version=config.APP_VERSION,
        model_loaded=loaded,
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
    """Dự đoán một URL bằng mô hình đã nạp (hoặc dữ liệu giả nếu PHISHING_MOCK=1)."""
    if config.MOCK_MODE:
        return PredictResponse(**predictor_module.predict_mock(request.url))
    return PredictResponse(**predictor_module.get_predictor().predict(request.url))
