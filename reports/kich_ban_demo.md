# Kịch bản demo (3–5 URL mẫu)

> Điền URL thật vào cột "URL" sau khi chạy thử với mô hình đã huấn luyện, chọn ví dụ mà mô hình cho kết quả ổn định.

| # | Loại | URL | Kết quả mong đợi |
| --- | --- | --- | --- |
| 1 | Hợp pháp | (một trang nổi tiếng, vd. https://www.wikipedia.org) | Khung xanh, rủi ro thấp |
| 2 | Phishing | (URL từ tập test được mô hình nhận đúng là phishing) | Khung đỏ, rủi ro cao, có danh sách dấu hiệu |
| 3 | Ca biên | (URL dài nhiều ký tự đặc biệt, hoặc dùng IP) | Mức trung bình/cao kèm dấu hiệu |
| 4 | Lỗi định dạng | `example.com` hoặc `abc def` | Cảnh báo ngay ở Frontend, không gọi API |
| 5 | Lỗi hệ thống | Tắt Backend rồi bấm "Kiểm tra an toàn" | "Không thể kết nối Backend" |

## Trình tự demo
1. Bật Backend và Frontend, mở giao diện.
2. Chạy URL 1 → 2 → 3, chỉ vào Risk Bar và danh sách dấu hiệu.
3. Nhập URL 4 để minh họa kiểm tra đầu vào.
4. Tắt Backend, chạy URL 5 để minh họa lỗi kết nối. Bật lại Backend.
5. (Tùy chọn) Mở Swagger UI, gửi cùng URL, đối chiếu kết quả.