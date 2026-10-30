# Phishing Detection

Hệ thống phát hiện website lừa đảo (phishing) dựa trên URL. Người dùng nhập một URL, hệ thống trích xuất đặc trưng từ chuỗi URL, dự đoán bằng mô hình học máy và trả về kết quả kèm độ tin cậy.

Dự án gồm 3 thành phần:

- **Machine Learning** (`notebooks/`, `artifacts/`): khám phá dữ liệu, huấn luyện và đánh giá mô hình.
- **Backend** (`backend/`): REST API bằng FastAPI, nạp mô hình và trả kết quả dạng JSON.
- **Frontend** (`frontend/`): giao diện Streamlit, gọi API và hiển thị kết quả.

## Tài nguyên cần tải từ Google Drive

Dữ liệu và file mô hình không có trên GitHub. Trước khi chạy notebook hoặc backend, tải toàn bộ từ thư mục Drive sau:

**Link Drive:** https://drive.google.com/drive/folders/1u75vZz8cUJKjFpQdxgbWS5FJ_rU80oEx?usp=drive_link

Sau khi tải, đặt file vào đúng vị trí:

| Thư mục | Nội dung |
|---|---|
| `data/raw/` | `URL_dataset.csv`, `Training_Dataset.arff` |
| `data/processed/` | Dữ liệu đã làm sạch và chia tập |
| `artifacts/` | `model.joblib`, `scaler.joblib` (nếu có) |

`artifacts/features.json` có sẵn trên GitHub, không cần tải lại.

## Cấu trúc thư mục

```
phishing-detection/
├── artifacts/                  # model.joblib, scaler.joblib (Drive); features.json (GitHub)
│   └── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Đường dẫn tới artifacts/ và data/
│   │   ├── feature_extractor.py
│   │   ├── main.py
│   │   ├── predictor.py
│   │   └── schemas.py
│   ├── tests/
│   └── README.md
├── data/                       # Không có trên GitHub, tải từ Drive
│   ├── raw/
│   └── processed/
├── experiments/
│   ├── experiment_log.csv
│   └── README.md
├── frontend/
│   ├── app.py
│   └── README.md
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_modeling.ipynb
│   └── 03_feature_extractor.ipynb
├── reports/
│   ├── figures/
│   └── results_summary.csv
├── .gitignore
├── README.md
└── requirements.txt
```

## Cài đặt môi trường

Mỗi thành viên tự tạo môi trường ảo trong thư mục gốc của dự án.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell báo lỗi quyền thực thi script, dùng Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Cài thư viện:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python được cố định ở phiên bản **3.12**.

## Chạy dự án

Trước khi chạy, đảm bảo đã tải đủ dữ liệu và artifacts từ Drive.

Chạy backend (từ thư mục gốc):

```bash
cd backend
uvicorn app.main:app --reload
```

API chạy tại `http://127.0.0.1:8000`. Tài liệu Swagger UI tại `http://127.0.0.1:8000/docs`.

Chạy frontend (mở terminal khác, từ thư mục gốc):

```bash
streamlit run frontend/app.py
```

## Dữ liệu

- `data/raw/` chứa file gốc. Không sửa tay. Mọi thay đổi đi qua notebook hoặc script.
- `data/processed/` chứa dữ liệu đã làm sạch và chia tập, dùng chung cho cả nhóm. Khi cập nhật, tải bản mới lên Drive và báo nhóm.

### Quy ước nhãn

| Hạng mục | Quy ước |
|---|---|
| Nhãn nội bộ | `1` = phishing, `0` = legitimate |
| Dataset UCI | `-1` = phishing (khác với quy ước nội bộ) |
| Ánh xạ nhãn | Chỉ ánh xạ ở một chỗ duy nhất, trong `feature_extractor.py` hoặc một hàm trong notebook |
| Chia tập | Chia theo `host`, `stratify` theo nhãn, `random_state=42` |

## Đặc trưng và mã hóa

Backend và notebook phải tạo ra đúng cùng một vector đặc trưng.

- **Danh sách đặc trưng:** lấy từ `artifacts/features.json`, giữ đúng thứ tự cột. Backend đọc file này khi khởi động, không tự định nghĩa lại.
- **Kiểu dữ liệu:** số hoặc boolean được mã hóa thành `0/1`. Ví dụ `has_ip` là `0/1`, không phải `true/false`.
- **Hàm trích xuất:** chỉ `backend/app/feature_extractor.py` được phép tính đặc trưng từ URL. Notebook và Backend đều import từ đó, không copy code.
- **Test bắt buộc:** `backend/tests/` kiểm tra `extract(url)` với vài URL mẫu để đảm bảo kết quả khớp kỳ vọng.

## API

### Endpoint

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `/health` | Kiểm tra trạng thái dịch vụ |
| POST | `/api/v1/predict` | Dự đoán một URL |

### Request

```json
{
  "url": "http://paypal.com.account-update.fake-domain.com/login"
}
```

### Response thành công (200 OK)

```json
{
  "url": "http://paypal.com.account-update.fake-domain.com/login",
  "prediction": "phishing",
  "is_phishing": true,
  "confidence": 0.96,
  "details": {
    "has_ip": false,
    "long_url": true,
    "has_at_symbol": false,
    "subdomain_count": 3,
    "has_prefix_suffix": true
  }
}
```

- `confidence` là xác suất của lớp phishing, trong khoảng 0 đến 1.
- Các khóa trong `details` phải khớp với đặc trưng hiển thị ở Frontend.

### Response lỗi (422)

```json
{
  "error": "INVALID_URL",
  "message": "Chuỗi nhập vào không phải định dạng URL hợp lệ."
}
```

Các mã lỗi hiện có:

| Mã | Ý nghĩa |
|---|---|
| `INVALID_URL` | URL sai định dạng |
| `EMPTY_URL` | URL rỗng |
| `URL_TOO_LONG` | URL vượt giới hạn độ dài |
| `MODEL_NOT_LOADED` | Mô hình chưa được nạp |

Frontend chỉ xử lý các mã lỗi trên.

### Phiên bản

API dùng tiền tố `/api/v1/`. Nếu thay đổi contract không tương thích ngược, tăng lên `/api/v2/`.

## Artifacts và mô hình

| File | Nguồn | Mô tả |
|---|---|---|
| `model.joblib` | Drive | Mô hình đã huấn luyện |
| `scaler.joblib` | Drive | Bộ chuẩn hóa (chỉ có nếu mô hình cuối là SVM) |
| `features.json` | GitHub | Danh sách đặc trưng theo đúng thứ tự cột |

- Dùng đúng tên file, không đổi tên.
- Phiên bản thư viện được cố định trong `requirements.txt`, đặc biệt là `scikit-learn`. File `.joblib` có thể không nạp được khi khác phiên bản.
- Mô hình được chọn và lý do chọn được ghi trong `artifacts/README.md`, kèm số liệu từ `reports/results_summary.csv`.

## Quy trình làm việc với Git

### Nhánh

| Nhánh | Mục đích |
|---|---|
| `main` | Code ổn định, dùng để demo |
| `dev` | Nhánh tích hợp chung |
| `feat/ml-training` | Thành viên ML |
| `feat/backend-api` | Thành viên Backend |
| `feat/frontend-ui` | Thành viên Frontend |

- Mọi cập nhật vào `dev` đi qua Pull Request.
- Không push trực tiếp lên `main`.
- Mỗi PR cần ít nhất một người khác review, đặc biệt là PR thay đổi `artifacts/` hoặc API.

### Commit message

Dùng một ngôn ngữ nhất quán trong toàn dự án, theo định dạng `loại(phạm vi): mô tả`. Ví dụ:

```
feat(backend): add /predict endpoint
```

## Quy ước code

- **Seed ngẫu nhiên:** `random_state=42` ở mọi nơi.
- **Đường dẫn:** quản lý trong `backend/app/config.py`, không ghi cứng đường dẫn tuyệt đối.
- **Ngôn ngữ comment:** tiếng Việt hoặc tiếng Anh, thống nhất trong toàn dự án.

## Thành viên nhóm

| Thành viên | Vai trò | Nhánh |
|---|---|---|
| | Machine Learning | `feat/ml-training` |
| | Backend API | `feat/backend-api` |
| | Frontend UI | `feat/frontend-ui` |
