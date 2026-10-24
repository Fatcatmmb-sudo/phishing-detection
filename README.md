# phishing-detection

 Mỗi thành viên cài trong thư mục gốc của project:
python -m venv .venv


Kích hoạt môi trường ảo trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1


Nếu PowerShell báo lỗi quyền thực thi script, có thể dùng Command Prompt và chạy:
.venv\Scripts\activate.bat


Sau đó cài thư viện:
python -m pip install --upgrade pip
pip install -r requirements.txt

Quy ước chung dự án Phishing Detection

1. Dữ liệu và nhãn
Hạng mục
Quy ước đề xuất
Nhãn nội bộ
1 = phishing, 0 = legitimate. Ghi rõ đây là quy ước nội bộ, khác với UCI (-1 = phishing).
Ánh xạ nhãn
Chỉ ánh xạ ở một chỗ duy nhất, trong feature_extractor.py hoặc một hàm trong notebook. Không ánh xạ lại ở nơi khác.
Tập chia
Chia theo host, stratify theo nhãn, random_state=42. Làm sạch và chia tập ra file trong data/processed/ để cả nhóm dùng chung một bản.
File gốc
data/raw/ chỉ chứa file gốc, không sửa tay. Mọi thay đổi đi qua notebook hoặc script.

3. Đặc trưng và mã hóa
Đây là phần quan trọng nhất, vì Backend và Notebook phải tạo ra đúng cùng một vector đặc trưng.
• Danh sách đặc trưng: một nguồn duy nhất là artifacts/features.json, giữ đúng thứ tự cột. Backend đọc file này khi khởi động, không tự định nghĩa lại.
• Kiểu dữ liệu: thống nhất số hoặc boolean. Ví dụ has_ip là 0/1, không phải true/false trong mô hình.
• Hàm trích xuất: chỉ feature_extractor.py được phép tính đặc trưng từ URL. Notebook và Backend đều import từ đó, không copy code.
• Test bắt buộc: bộ test kiểm tra extract(url) với vài URL mẫu, đảm bảo kết quả khớp kỳ vọng. Đặt trong backend/tests/.\

5. API Contract
• confidence: là xác suất của lớp phishing (predict_proba()[:, 1]). Frontend Risk Bar dùng thang 0 đến 1 thống nhất.
• details: các khóa trong details phải khớp với đặc trưng hiển thị ở Frontend. Ví dụ has_prefix_suffix phải có cùng tên ở cả hai phía.
• Mã lỗi: liệt kê đầy đủ các error có thể trả về, ví dụ INVALID_URL, EMPTY_URL, MODEL_NOT_LOADED. Frontend chỉ xử lý những mã này.
• Phiên bản API: giữ /api/v1/. Nếu đổi contract thì tăng lên /api/v2/.

7. Artifacts và mô hình
• Tên file: model.joblib, scaler.joblib, features.json. Dùng đúng tên này, không đổi.
• Phiên bản thư viện: cố định phiên bản trong requirements.txt, đặc biệt là scikit-learn, vì file .joblib có thể không nạp được nếu khác phiên bản.
• Mô hình cuối: ghi rõ mô hình nào được chọn và lý do trong artifacts/README.md, kèm số liệu từ reports/results_summary.csv.

9. Git và cộng tác
• Nhánh: main chỉ chứa code ổn định để demo. dev là nhánh tích hợp. Nhánh cá nhân: feat/ml-training, feat/backend-api, feat/frontend-ui. Mọi cập nhật vào dev đi qua Pull Request.
• Commit message: chọn một ngôn ngữ và giữ nhất quán. Ví dụ feat(backend): add /predict endpoint.
• Review: mỗi PR cần ít nhất một người khác xem, đặc biệt là PR thay đổi artifacts/ hoặc API Contract.

11. Môi trường
• Python: cố định phiên bản 3.12, ghi trong README.
• Chạy thử: README của dự án có các lệnh chạy được ngay: tạo .venv, cài requirements, chạy backend, chạy frontend.

12. Quy ước code nhỏ
• Seed ngẫu nhiên: đặt random_state=42 ở mọi nơi.
• Đường dẫn: dùng config.py để quản lý đường dẫn tới artifacts/ và data/, không ghi cứng đường dẫn tuyệt đối.
• Ngôn ngữ comment: chọn tiếng Việt hoặc tiếng Anh, dùng thống nhất trong toàn dự án.
