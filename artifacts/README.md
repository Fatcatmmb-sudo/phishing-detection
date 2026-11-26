# Kết quả chọn mô hình

## Mô hình được chọn

Mô hình được chọn cho API và báo cáo ML là **Random Forest** với 120 cây,
`min_samples_leaf=2`, `random_state=42` và đủ 10 đặc trưng. Mô hình có F1
Validation cao nhất trong các mô hình so sánh đáp ứng Recall Validation ít nhất
0,95 và hỗ trợ `predict_proba` cho confidence của API.

| Tập | Accuracy | Precision phishing | Recall phishing | F1 phishing |
|---|---:|---:|---:|---:|
| Validation | 0,9923 | 0,9961 | 0,9706 | 0,9832 |
| Test | 0,9776 | 0,9957 | 0,9074 | 0,9495 |

Mô hình được lưu tại `selected_model.joblib`; `backend/app/config.py` trỏ API tới
file này. Recall Test thấp hơn Validation đáng kể, vì vậy cần trình bày hạn chế
này và tiếp tục theo dõi khả năng bỏ sót phishing.

Các hạn chế về lối tắt HTTPS, nhãn có thể lỗi thời và thiên lệch domain được
trình bày trong `reports/experiment_findings.md`.

## Tài nguyên

Dữ liệu nguồn và artifacts dùng chung của dự án: [thư mục Google Drive](https://drive.google.com/drive/folders/1u75vZz8cUJKjFpQdxgbWS5FJ_rU80oEx?usp=drive_link).

Kết quả đầy đủ: `experiments/experiment_log.csv`,
`reports/results_summary.csv` và `reports/final_evaluation.json`.
