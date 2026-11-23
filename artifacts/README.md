# Kết quả chọn mô hình

Thí nghiệm được chạy bằng `experiments/run_experiments.py`. Toàn bộ kết quả
Validation nằm trong `reports/results_summary.csv`; đánh giá holdout cuối nằm
trong `reports/final_evaluation.json`.

- Random Forest 120 cây đạt Validation F1 phishing **0,9832**, Precision
  **0,9961**, Recall **0,9706**.
- Trên Test, mô hình đạt Accuracy **0,9776**, Precision phishing **0,9957**,
  Recall **0,9074**, F1 **0,9495**.
- Mô hình này được lưu ở `selected_model.joblib` để xem xét. Chưa thay mô hình
  đang dùng bởi API: Recall trên Test giảm đáng kể so với Validation và cần
  được đánh giá theo yêu cầu nghiệp vụ trước khi triển khai.

Mô hình API hiện tại tiếp tục được trỏ bởi `backend/app/config.py`.
