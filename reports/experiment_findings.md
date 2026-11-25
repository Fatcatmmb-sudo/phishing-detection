# Tổng kết thực nghiệm

Các thử nghiệm dùng `train.csv` để fit và `validation.csv` để so sánh cấu hình.
`test.csv` chỉ được dùng một lần sau khi chọn cấu hình, để ước lượng kết quả
cuối. Chạy lại bằng `python experiments/run_experiments.py` trong môi trường dự án.

## Kết quả chính

- **Baseline EXP001:** Validation F1 phishing 0,9687; Recall 0,9739.
- **Giảm độ phức tạp cây:** tốt nhất là `max_depth=15`, Validation F1 0,9816,
  Precision 0,9940, Recall 0,9696. Accuracy Train giảm so với baseline, cho thấy
  khoảng cách Train/Validation nhỏ hơn.
- **Cân bằng lớp:** `class_weight="balanced"` tăng Recall Validation rất ít
  (0,9740 so với 0,9739) nhưng Precision giảm từ 0,9636 xuống 0,9384 và F1 giảm
  xuống 0,9559. Với kết quả này chưa có lợi thế rõ ràng.
- **Đặc trưng:** nhóm `has_https` riêng có F1 0,9732, nhưng Recall chỉ 0,9482.
  Bỏ nhóm này làm F1 giảm mạnh còn 0,7043. Các nhóm độ dài, cấu trúc hostname,
  và ký tự đặc biệt riêng lẻ đều yếu; các đặc trưng phối hợp mới cho kết quả tốt.
- **Thuật toán:** Random Forest đạt F1 Validation cao nhất (0,9832), kế đến
  Decision Tree `max_depth=15` (0,9816). LinearSVC đạt 0,9744 nhưng không cung
  cấp `predict_proba` trực tiếp như contract confidence của API hiện tại.

## Đánh giá cuối

Random Forest được chọn theo F1 Validation cao nhất trong các mô hình dùng đủ 10
đặc trưng, có `predict_proba` và Recall Validation ít nhất 0,95. Trên Test, mô
hình đạt Accuracy **0,9776**, Precision phishing **0,9957**, Recall phishing
**0,9074**, F1 phishing **0,9495**. Recall thấp hơn đáng kể so với Validation;
đây là dấu hiệu cần điều tra khả năng khác biệt phân phối giữa các host/tập dữ
liệu trước khi thay mô hình API.

Mô hình ứng viên nằm ở `artifacts/selected_model.joblib`. API hiện tiếp tục dùng
baseline theo `backend/app/config.py`; không tự động đổi mô hình đang chạy.
