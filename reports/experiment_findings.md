# Tổng kết thực nghiệm ML

Các mô hình được huấn luyện trên `train.csv`; cấu hình được so sánh trên
`validation.csv`. Tập `test.csv` chỉ dùng cho đánh giá cuối cùng của mô hình
ứng viên, không dùng để chọn cấu hình. EXP020 là lần chạy lại baseline để kiểm
tra tính lặp lại; kết quả khớp EXP001. EXP021 đã được chạy lại trong notebook và
khớp nhật ký.

## So sánh mô hình

Các chỉ số dưới đây tính cho lớp phishing trên Validation.

| Thí nghiệm | Mô hình/cấu hình | Số đặc trưng | Accuracy | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|
| EXP001 | Decision Tree mặc định | 10 | 0,9854 | 0,9636 | 0,9739 | 0,9687 |
| EXP003 | Decision Tree, `max_depth=15` | 10 | 0,9916 | 0,9940 | 0,9696 | 0,9816 |
| EXP009 | Decision Tree, `class_weight=balanced` | 10 | 0,9791 | 0,9384 | 0,9740 | 0,9559 |
| EXP018 | Random Forest, 120 cây, `min_samples_leaf=2` | 10 | 0,9923 | 0,9961 | 0,9706 | **0,9832** |
| EXP019 | LinearSVC với StandardScaler | 10 | 0,9884 | 0,9985 | 0,9515 | 0,9744 |

Random Forest có F1 Validation cao nhất trong các mô hình dùng đủ 10 đặc trưng
có `predict_proba` và Recall ít nhất 0,95. LinearSVC không cung cấp
`predict_proba` trực tiếp trong cấu hình này nên không đáp ứng trực tiếp hợp
đồng confidence hiện tại của API.

## Độ phức tạp và mất cân bằng

Trong các cấu hình Decision Tree đã thử, `max_depth=15` đạt F1 Validation
0,9816; khoảng cách Accuracy Train/Validation nhỏ hơn baseline.
`class_weight="balanced"` tăng Recall chỉ nhẹ (0,9739 lên 0,9740), trong khi
Precision và F1 giảm đáng kể; cấu hình này chưa cho lợi ích tổng thể rõ ràng.

## Đóng góp của đặc trưng và lối tắt HTTPS

EXP021 giữ nguyên cấu hình Random Forest của EXP018 nhưng bỏ `has_https`. F1
Validation giảm từ 0,9832 xuống **0,7664**, Recall từ 0,9706 xuống **0,7427**.
Với Decision Tree, chỉ dùng `has_https` đạt F1 0,9732; bỏ HTTPS khỏi bộ đặc
trưng làm F1 giảm còn 0,7043. Kết quả cho thấy tín hiệu HTTPS có ảnh hưởng lớn
trong bộ dữ liệu này và có thể là một lối tắt mà mô hình dựa vào.

Phân tích lỗi trên Test cho thấy 100% URL phishing bị bỏ sót (false negative)
dùng HTTPS, so với khoảng 2,26% URL phishing được phát hiện đúng. Đây là tương
quan trong tập dữ liệu, không chứng minh HTTPS là nguyên nhân duy nhất của lỗi
hay rằng HTTPS tự nó là dấu hiệu an toàn.

## Đánh giá cuối và hạn chế

Random Forest ứng viên đạt trên Test: Accuracy **0,9776**, Precision phishing
**0,9957**, Recall phishing **0,9074**, F1 phishing **0,9495**. Recall Test thấp
hơn Recall Validation (0,9706), nên cần xem xét khác biệt phân phối trước khi
đổi mô hình đang phục vụ API. API hiện tiếp tục dùng Decision Tree baseline.

Các hạn chế cần nêu khi trình bày:

- **Lối tắt HTTPS:** nhãn trong dữ liệu tương quan rất mạnh với `has_https`; mô
  hình có thể học tín hiệu thu thập dữ liệu thay vì đặc điểm phishing bền vững.
- **Nhãn có thể lỗi thời:** URL và website thay đổi trạng thái theo thời gian;
  nhãn trong bộ dữ liệu tĩnh có thể không còn đúng tại thời điểm sử dụng.
- **Thiên lệch domain nổi tiếng:** bộ dữ liệu có thể đại diện quá nhiều hoặc quá
  ít cho một số domain phổ biến. Đây là nguy cơ cần kiểm tra thêm bằng đánh giá
  theo domain và dữ liệu độc lập; các thực nghiệm hiện tại chưa đo riêng mức
  thiên lệch này.

Xem đầy đủ các cấu hình tại `experiments/experiment_log.csv` và
`reports/results_summary.csv`. Đánh giá cuối được lưu ở
`reports/final_evaluation.json`.
