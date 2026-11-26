# Frontend – Phishing Website Detection

## 1. Giới thiệu

Frontend được xây dựng bằng **Streamlit**, cung cấp giao diện cho người dùng nhập URL và kiểm tra website có dấu hiệu lừa đảo (phishing) hay không.

Frontend giao tiếp với Backend thông qua REST API sử dụng HTTP POST.

## 2. Công nghệ sử dụng

- Python 3.12
- Streamlit
- Requests
- Pytest (chạy test)

## 3. Chức năng

- Nhập URL cần kiểm tra; kiểm tra sơ bộ (không trống, không có khoảng trắng, bắt đầu bằng `http://` hoặc `https://`) trước khi gọi API.
- Gửi URL đến Backend FastAPI.
- Hiển thị kết quả bằng khung màu: đỏ (phishing) hoặc xanh (an toàn) theo `is_phishing`.
- Hiển thị mức độ rủi ro phishing dưới dạng phần trăm và Risk Bar, chia 3 mức: thấp (< 40%), trung bình (40% – dưới 70%), cao (≥ 70%).
- Hiển thị danh sách dấu hiệu từ `details`, mỗi khóa có nhãn tiếng Việt.
- Thông báo thân thiện cho: URL trống hoặc sai định dạng, `INVALID_URL` (422), `MODEL_NOT_LOADED` (503), timeout, mất kết nối Backend.

## 4. Cấu trúc

```text
frontend/
├── app.py              # Giao diện Streamlit
├── logic.py            # Hàm xử lý logic thuần (đọc cấu hình, kiểm tra URL, mức rủi ro, nhãn, thông báo lỗi)
└── README.md

tests/
└── test_frontend_logic.py   # Unit test cho frontend/logic.py
```

## 5. Cách chạy

### Bước 1: Cài đặt

Tại thư mục gốc dự án, kích hoạt môi trường ảo (Python 3.12):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Bước 2: Khởi động Backend

Mặc định Backend **nạp mô hình thật** (cần các file trong `artifacts/`: `selected_model.joblib`, `features.json`).

Mở Terminal thứ nhất:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend chạy tại `http://127.0.0.1:8000`.

Chỉ khi muốn dữ liệu giả (chưa có mô hình), đặt biến môi trường `PHISHING_MOCK=1` **trước khi** chạy Backend:

```powershell
$env:PHISHING_MOCK = "1"
python -m uvicorn app.main:app --reload
```

### Bước 3: Khởi động Frontend

Mở Terminal thứ hai tại thư mục gốc dự án:

```powershell
python -m streamlit run frontend/app.py
```

Streamlit sẽ cung cấp địa chỉ truy cập giao diện trên trình duyệt.

### Đổi địa chỉ Backend (tùy chọn)

Địa chỉ Backend đọc từ biến môi trường `BACKEND_URL`, mặc định `http://127.0.0.1:8000`:

```powershell
$env:BACKEND_URL = "http://192.168.1.10:8000"
python -m streamlit run frontend/app.py
```

(macOS/Linux: `export BACKEND_URL=http://192.168.1.10:8000`)

## 6. Chạy test

```powershell
python -m pytest tests/test_frontend_logic.py
```

## 7. API sử dụng

**Endpoint:**

`POST /api/v1/predict`

**Request:**

```json
{
  "url": "https://example.com"
}
```

**Response:**

```json
{
  "url": "https://www.wikipedia.org/",
  "prediction": "legitimate",
  "is_phishing": false,
  "confidence": 0.007767362308319675,
  "details": {
    "url_length": 26,
    "hostname_length": 17,
    "dot_count": 2,
    "hyphen_count": 0,
    "digit_count": 0,
    "at_count": 0,
    "slash_count": 3,
    "question_count": 0,
    "equal_count": 0,
    "has_https": true
  }
}
```

Trong đó `confidence` là xác suất thuộc lớp phishing, có giá trị từ 0 đến 1. Frontend lấy dấu hiệu từ `details` (không dùng `extracted_features`).

**Lỗi:** Backend trả JSON dạng `{"error": "<MÃ_LỖI>", "message": "..."}`:

| HTTP | `error` | Frontend hiển thị |
| --- | --- | --- |
| 422 | `INVALID_URL` | "URL không hợp lệ: ..." |
| 503 | `MODEL_NOT_LOADED` | "Mô hình chưa được tải..." |
| Timeout | – | "Yêu cầu quá thời gian chờ..." |
| Mất kết nối | – | "Không thể kết nối Backend..." |

## 8. Lưu ý

- Kết quả là dự đoán của mô hình, không đảm bảo website an toàn tuyệt đối.
- Nếu Backend chạy chế độ `PHISHING_MOCK=1`, kết quả chỉ để kiểm tra luồng, chưa đại diện cho hiệu năng mô hình thật.
- Không ghi đường dẫn cá nhân vào code; mọi cấu hình đi qua biến môi trường.
