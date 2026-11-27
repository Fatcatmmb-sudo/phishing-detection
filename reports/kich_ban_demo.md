# Kịch bản demo – Phishing Website Detection

## 1. Danh sách URL kiểm thử thực tế

| # | Loại | URL / Dữ liệu kiểm thử | Kết quả thực tế | Đánh giá |
|---|---|---|---|---|
| 1 | Hợp pháp | `https://www.wikipedia.org` | SAFE, rủi ro 2%, khung xanh | PASS |
| 2 | Phishing | `http://atualizacaodedados.online` | PHISHING, rủi ro 100%, khung đỏ | PASS |
| 3 | Ca biên – IP | `http://174.142.5.14/bs3/js/perm:pe4` | PHISHING, rủi ro 100%, khung đỏ | PASS |
| 4 | Lỗi định dạng | `example.com` | Hiển thị: "URL phải bắt đầu bằng http:// hoặc https://." | PASS |
| 5 | Lỗi hệ thống | Tắt Backend rồi kiểm tra URL hợp lệ | Hiển thị: "Không kết nối được tới Backend. Hãy kiểm tra Backend đã chạy chưa." | PASS |

## 2. Kiểm tra Backend

Sau khi bật lại Backend, gọi endpoint `/health`:

| Trường | Kết quả |
|---|---|
| status | `ok` |
| version | `0.1.0` |
| model_loaded | `True` |
| mock_mode | `False` |

Kết luận: Backend hoạt động bình thường và đang sử dụng mô hình thật, không sử dụng Mock.

## 3. Trường hợp dự đoán sai cần lưu ý

| URL | Kết quả thực tế |
|---|---|
| `https://google.com` | Mô hình dự đoán PHISHING với rủi ro 91.7%, trong khi đây là website hợp pháp |

Đây là trường hợp False Positive (dương tính giả). Không sử dụng URL này làm ví dụ demo thành công. Cần ghi nhận trong phần hạn chế của mô hình và báo lại thành viên phụ trách ML.

## 4. Trình tự demo

1. Bật Backend với `PHISHING_MOCK=0`.
2. Kiểm tra `/health`, xác nhận `model_loaded=True` và `mock_mode=False`.
3. Bật Frontend bằng Streamlit và mở giao diện.
4. Nhập URL số 1 để minh họa website hợp pháp.
5. Nhập URL số 2 và số 3 để minh họa website phishing.
6. Nhập URL số 4 để minh họa kiểm tra định dạng đầu vào.
7. Tắt Backend, nhập URL hợp lệ và kiểm tra thông báo lỗi kết nối.
8. Bật lại Backend và xác nhận dịch vụ hoạt động.
9. (Tùy chọn) Mở Swagger UI để đối chiếu kết quả API.

## 5. Ghi chú

- Kết quả rủi ro là điểm dự đoán do mô hình cung cấp, không phải xác suất chắc chắn tuyệt đối.
- Các URL phishing lấy từ tập kiểm thử đã gán nhãn.
- Không truy cập trực tiếp các URL phishing trong quá trình demo; chỉ nhập URL để hệ thống phân tích.
- Trường hợp Google bị dự đoán nhầm cần được giữ lại trong báo cáo đánh giá mô hình.