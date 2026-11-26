# Checklist End-to-End

Người chạy: ______  Ngày: ______  Máy: ______

| # | Bước | Kỳ vọng | Kết quả thực tế | Đạt? |
| --- | --- | --- | --- | --- |
| 1 | Clone repo, cài đặt theo README trên máy sạch | Không phụ thuộc đường dẫn cá nhân | | ☐ |
| 2 | Chạy Backend (mô hình thật) | `GET /health` trả 200 | | ☐ |
| 3 | Chạy Frontend | Trang mở được | | ☐ |
| 4 | Nhập URL hợp pháp trên Frontend | Khung xanh, rủi ro thấp | | ☐ |
| 5 | Gửi cùng URL trên Swagger `POST /api/v1/predict` | `is_phishing`, `confidence` khớp bước 4 | | ☐ |
| 6 | Nhập URL phishing trên Frontend | Khung đỏ, có dấu hiệu từ `details` | | ☐ |
| 7 | Gửi cùng URL trên Swagger | Khớp bước 6 | | ☐ |
| 8 | Nhập URL sai định dạng | Thông báo lỗi thân thiện | | ☐ |
| 9 | Tắt Backend, bấm kiểm tra | Thông báo mất kết nối | | ☐ |
| 10 | Chạy `python -m pytest tests` | Tất cả pass | | ☐ |

## Quy trình Git
- [ ] Tạo PR `feat/frontend-*` → `dev`, có ít nhất 1 người review
- [ ] Merge `dev` → `main` sau khi checklist trên đạt
- [ ] `main` chạy được trên một máy mới theo README
### Trạng thái sau khi chuyển sang Random Forest

- API được cấu hình nạp `artifacts/selected_model.joblib`.
- Tệp mô hình có trong thư mục artifacts tại máy phát triển.
- Các kiểm tra API trước đây được thực hiện với Decision Tree baseline; cần
  khởi động lại Backend và xác nhận lại `GET /health` cùng một dự đoán mẫu sau
  khi đổi mô hình.
- Điền kết quả thực tế và lưu ảnh minh chứng sau lần kiểm tra mới; không dùng
  trạng thái BLOCKED cũ vì trạng thái đó ghi sai tên artifact và đã lỗi thời.
