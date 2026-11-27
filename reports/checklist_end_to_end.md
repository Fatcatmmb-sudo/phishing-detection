<!-- # Checklist End-to-End

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
  trạng thái BLOCKED cũ vì trạng thái đó ghi sai tên artifact và đã lỗi thời. -->

# Checklist End-to-End

Người chạy: **\_\_**  
Ngày: 27/11/2026  
Máy: Máy phát triển Windows

| #   | Bước                                             | Kỳ vọng                                 | Kết quả thực tế                                                                                                                  | Đạt? |
| --- | ------------------------------------------------ | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---- |
| 1   | Clone repo, cài đặt theo README trên máy sạch    | Không phụ thuộc đường dẫn cá nhân       | Chưa thực hiện kiểm thử trên máy sạch                                                                                            | ☐    |
| 2   | Chạy Backend (mô hình thật)                      | `GET /health` trả 200                   | `status=ok`, `version=0.1.0`, `model_loaded=True`, `mock_mode=False`                                                             | ☑    |
| 3   | Chạy Frontend                                    | Trang mở được                           | Streamlit mở giao diện và thực hiện kiểm tra URL thành công                                                                      | ☑    |
| 4   | Nhập URL hợp pháp trên Frontend                  | Khung xanh, rủi ro thấp                 | `https://www.wikipedia.org` → SAFE, rủi ro 2%                                                                                    | ☑    |
| 5   | Gửi cùng URL trên Swagger `POST /api/v1/predict` | `is_phishing`, `confidence` khớp bước 4 | Chưa kiểm tra Swagger                                                                                                            | ☐    |
| 6   | Nhập URL phishing trên Frontend                  | Khung đỏ, có dấu hiệu từ `details`      | `http://atualizacaodedados.online` → PHISHING, rủi ro 100%; URL IP `http://174.142.5.14/bs3/js/perm:pe4` → PHISHING, rủi ro 100% | ☑    |
| 7   | Gửi cùng URL trên Swagger                        | Khớp bước 6                             | Kiểm thử API khi model chưa được tải. API trả HTTP 503. Error code là MODEL_NOT_LOADED. Response có thông báo lỗi rõ ràng.Swagger                                                                                                            | ☑    |
| 8   | Nhập URL sai định dạng                           | Thông báo lỗi thân thiện                | `example.com` → "URL phải bắt đầu bằng http:// hoặc https://."                                                                   | ☑    |
| 9   | Tắt Backend, bấm kiểm tra                        | Thông báo mất kết nối                   | Hiển thị "Không kết nối được tới Backend. Hãy kiểm tra Backend đã chạy chưa." Sau đó Backend đã được bật lại và health trả về OK | ☑    |
| 10  | Chạy `python -m pytest tests`                    | Tất cả pass                             | 85 tests passed                                                                                                                  | ☑    |

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
- Đã kiểm tra lỗi định dạng URL và lỗi mất kết nối Backend.
- Phát hiện False Positive: `https://google.com` bị mô hình dự đoán PHISHING với rủi ro 91.7%. Cần báo lại thành viên phụ trách ML và ghi nhận trong phần hạn chế mô hình.
- Cần bổ sung kiểm tra Swagger và chạy toàn bộ `python -m pytest tests` trước khi hoàn tất checklist.

## Kết luận

Frontend đã kiểm thử được với Backend sử dụng Random Forest thật ở các trường hợp URL hợp pháp, phishing, URL sai định dạng và Backend mất kết nối.

Checklist chưa hoàn tất End-to-End vì còn thiếu kiểm thử Swagger, chạy toàn bộ test suite và xác nhận triển khai trên máy sạch.
