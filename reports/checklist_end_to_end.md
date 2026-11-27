# Checklist End-to-End

Người chạy: **\_\_**  
Ngày: 27/11/2026  
Máy: Máy phát triển Windows

| # | Bước | Kỳ vọng | Kết quả thực tế | Đạt? |
|---|---|---|---|---|
| 1 | Clone repo, cài đặt theo README trên máy sạch | Không phụ thuộc đường dẫn cá nhân | Chưa thực hiện kiểm thử trên máy sạch | ☐ |
| 2 | Chạy Backend (mô hình thật) | `GET /health` trả 200 | `status=ok`, `version=0.1.0`, `model_loaded=True`, `mock_mode=False` | ☑ |
| 3 | Chạy Frontend | Trang mở được | Streamlit mở giao diện và thực hiện kiểm tra URL thành công | ☑ |
| 4 | Nhập URL hợp pháp trên Frontend | Khung xanh, rủi ro thấp | `https://www.wikipedia.org` → SAFE, rủi ro 2% | ☑ |
| 5 | Gửi cùng URL trên Swagger `POST /api/v1/predict` | `is_phishing`, `confidence` khớp bước 4 | Wikipedia → HTTP 200, dự đoán legitimate, confidence khoảng 1.9% | ☑ |
| 6 | Nhập URL phishing trên Frontend | Khung đỏ, có dấu hiệu từ `details` | `http://atualizacaodedados.online` → PHISHING, rủi ro 100%; URL IP `http://174.142.5.14/bs3/js/perm:pe4` → PHISHING, rủi ro 100% | ☑ |
| 7 | Kiểm tra API khi model chưa được tải trên Swagger | API trả lỗi rõ ràng | API trả HTTP 503, error code `MODEL_NOT_LOADED`, có thông báo lỗi rõ ràng | ☑ |
| 8 | Nhập URL sai định dạng | Thông báo lỗi thân thiện | `example.com` → "URL phải bắt đầu bằng http:// hoặc https://." | ☑ |
| 9 | Tắt Backend, bấm kiểm tra | Thông báo mất kết nối | Hiển thị "Không kết nối được tới Backend. Hãy kiểm tra Backend đã chạy chưa." Sau đó Backend đã được bật lại và health trả về OK | ☑ |
| 10 | Kiểm tra Timeout trên Frontend | Hiển thị thông báo máy chủ phản hồi quá chậm | Dùng API giả lập phản hồi sau 15 giây; Frontend timeout sau 10 giây và hiển thị "Máy chủ phản hồi quá chậm. Vui lòng thử lại." | ☑ |
| 11 | Chạy `python -m pytest tests` | Tất cả pass | 85 tests passed, 1 warning, 0 failed | ☑ |

## Quy trình Git

- [ ] Tạo PR `feat/frontend-*` → `dev`, có ít nhất 1 người review
- [ ] Merge `dev` → `main` sau khi checklist trên đạt
- [ ] `main` chạy được trên một máy mới theo README

## Trạng thái sau khi chuyển sang Random Forest

- API được cấu hình nạp `artifacts/selected_model.joblib`.
- Tệp mô hình đã có trong thư mục artifacts tại máy phát triển.
- Backend đã được khởi động với `PHISHING_MOCK=0`.
- `GET /health` xác nhận `model_loaded=True`, `mock_mode=False`.
- Đã kiểm tra dự đoán thực tế trên Frontend:
  - `https://www.wikipedia.org`: SAFE, rủi ro 2%.
  - `http://atualizacaodedados.online`: PHISHING, rủi ro 100%.
  - `http://174.142.5.14/bs3/js/perm:pe4`: PHISHING, rủi ro 100%.
- Đã kiểm tra Swagger:
  - URL hợp pháp trả HTTP 200.
  - URL phishing trả HTTP 200.
  - Khi model chưa được tải, API trả HTTP 503 với `MODEL_NOT_LOADED`.
- Đã kiểm tra lỗi định dạng URL và lỗi mất kết nối Backend.
- Đã kiểm thử Timeout Frontend thành công bằng API giả lập:
  - API giả lập chờ 15 giây trước khi phản hồi.
  - Frontend cấu hình timeout 10 giây.
  - Frontend hiển thị đúng thông báo timeout.
  - Đã dừng các tiến trình kiểm thử và xóa file `slow_api.py`.
- Đã chạy `python -m pytest tests`: 85 passed, 1 warning.
- Phát hiện False Positive: `https://google.com` bị mô hình dự đoán PHISHING với rủi ro 91.7%. Cần báo lại thành viên phụ trách ML và ghi nhận trong phần hạn chế mô hình.

## Kết luận

Frontend đã được kiểm thử với Backend sử dụng Random Forest thật ở các trường hợp URL hợp pháp, phishing, URL sai định dạng, Backend mất kết nối và model chưa được tải.

Chức năng Timeout trên Frontend cũng đã được kiểm thử thành công bằng API giả lập. Toàn bộ 85 automated tests đều passed.

Checklist vẫn chưa hoàn tất End-to-End toàn nhóm vì còn cần xác nhận chạy trên máy sạch, hoàn thành PR/review và quy trình merge `dev` → `main`.