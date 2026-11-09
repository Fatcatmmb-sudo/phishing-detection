# Frontend – Phishing Website Detection

## 1. Giới thiệu

Frontend được xây dựng bằng **Streamlit**, cung cấp giao diện cho người dùng nhập URL và kiểm tra website có dấu hiệu lừa đảo (phishing) hay không.

Frontend giao tiếp với Backend thông qua REST API sử dụng HTTP POST.

## 2. Công nghệ sử dụng

- Python 3.11
- Streamlit
- Requests

## 3. Chức năng

- Nhập URL cần kiểm tra.
- Gửi URL đến Backend FastAPI.
- Hiển thị kết quả: SAFE hoặc PHISHING.
- Hiển thị mức độ rủi ro phishing dưới dạng phần trăm.
- Hiển thị các đặc trưng được trích xuất từ URL.
- Xử lý các trường hợp URL trống, URL không hợp lệ và lỗi kết nối Backend.

## 4. Cấu trúc

```text
frontend/
├── app.py
└── README.md
```

## 5. Cách chạy

### Bước 1: Kích hoạt môi trường ảo

Tại thư mục gốc dự án:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Bước 2: Khởi động Backend

Mở Terminal thứ nhất:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend chạy tại:

`http://127.0.0.1:8000`

### Bước 3: Khởi động Frontend

Mở Terminal thứ hai tại thư mục gốc dự án:

```powershell
python -m streamlit run frontend/app.py
```

Streamlit sẽ cung cấp địa chỉ truy cập giao diện trên trình duyệt.

## 6. API sử dụng

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
  "url": "https://example.com",
  "prediction": "legitimate",
  "is_phishing": false,
  "confidence": 0.05,
  "details": {}
}
```

Trong đó `confidence` là xác suất thuộc lớp phishing, có giá trị từ 0 đến 1.

## 7. Lưu ý

Hiện tại Backend đang sử dụng chế độ MOCK để kiểm tra luồng hoạt động và tích hợp Frontend–Backend. Kết quả chưa đại diện cho hiệu năng của mô hình Machine Learning thực tế.
