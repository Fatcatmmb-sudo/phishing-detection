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
### Test: Kiểm tra trạng thái API thật

- **Endpoint:** `GET /health`
- **HTTP Status:** `200 OK`
- **mock_mode:** `False`
- **model_loaded:** `False`
- **Expected:** Model được nạp thành công.
- **Actual:** Backend hoạt động nhưng không nạp được model.
- **Result:** BLOCKED
- **Reason:** Thiếu file `artifacts/decision_tree_baseline.joblib`.

**Ghi chú:** Đã tắt Mock và khởi động Backend thành công. Chưa thể kiểm thử dự đoán bằng model thật do thiếu artifact triển khai.

**Ảnh minh chứng:** Lưu ảnh kết quả PowerShell `/health` kèm theo báo cáo.