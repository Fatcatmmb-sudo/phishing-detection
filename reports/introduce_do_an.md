# Giới thiệu đồ án: Phát hiện URL phishing bằng Machine Learning

Tài liệu này giúp nhóm giới thiệu đồ án trong khoảng 3–5 phút. Phần **Bài nói
mẫu** có thể đọc gần như nguyên văn; các phần còn lại dùng để giải thích khi
thầy cô hỏi.

## Bài nói mẫu

> Xin chào thầy cô và các bạn. Nhóm em thực hiện đồ án phát hiện URL phishing
> bằng Machine Learning. Phishing là hình thức tạo đường dẫn hoặc trang web giả
> nhằm dụ người dùng cung cấp thông tin.
>
> Thay vì chỉ xây dựng một mô hình, nhóm em làm một luồng hoàn chỉnh: làm sạch
> dữ liệu URL, trích xuất 10 đặc trưng như độ dài URL, số ký tự đặc biệt và dấu
> hiệu HTTPS, huấn luyện và so sánh nhiều mô hình, sau đó cung cấp kết quả qua
> API FastAPI và giao diện Streamlit.
>
> Nhóm chia dữ liệu theo hostname để giảm nguy cơ cùng một domain xuất hiện ở
> cả tập huấn luyện và tập đánh giá. Trong các mô hình thử nghiệm, Random Forest
> có F1 cao nhất trên Validation, đạt 0,983. Trên Test, F1 là 0,950 và Recall
> phishing là 0,907. Kết quả này cũng giúp nhóm nhận ra một hạn chế quan trọng:
> mô hình có thể dựa quá nhiều vào HTTPS, nên nhóm không xem điểm số cao là
> bằng chứng rằng hệ thống đã có thể nhận diện mọi trang lừa đảo.
>
> Đồ án hiện là nguyên mẫu hỗ trợ nhận diện dựa trên URL. Nó không truy cập hay
> kiểm tra nội dung thực tế của website và không thay thế các biện pháp bảo mật
> khác. Qua đồ án, nhóm học được cách nối dữ liệu, mô hình, API và giao diện,
> đồng thời phải đánh giá Recall và phân tích lỗi chứ không chỉ nhìn Accuracy.

## Nhóm đã xây dựng những gì?

1. **Chuẩn bị dữ liệu:** chuẩn hóa URL, tách hostname, kiểm tra URL lỗi và chia
   Train/Validation/Test theo hostname. Cách chia này giúp hạn chế việc mô hình
   chỉ ghi nhớ những domain đã gặp khi huấn luyện.
2. **Trích xuất 10 đặc trưng:** độ dài URL và hostname; số dấu chấm, gạch ngang,
   chữ số, `@`, `/`, `?`, `=`; và URL có dùng HTTPS hay không.
3. **Thực nghiệm mô hình:** Decision Tree baseline, các cấu hình giảm độ phức
   tạp cây, `class_weight='balanced'`, ablation đặc trưng, Random Forest và
   LinearSVC. Nhật ký có 21 runs trong MLflow và bảng kết quả CSV.
4. **Tích hợp thành ứng dụng:** FastAPI nhận URL và trả nhãn, confidence cùng
   các đặc trưng; Streamlit cho phép nhập URL qua giao diện. API cũng xử lý URL
   sai định dạng và URL vượt giới hạn độ dài.

## Số liệu nên trình bày

Các chỉ số Precision, Recall và F1 dưới đây tính cho lớp phishing.

| Mô hình/kết quả | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Decision Tree baseline — Validation | 0,9854 | 0,9636 | 0,9739 | 0,9687 |
| Random Forest — Validation | 0,9923 | 0,9961 | 0,9706 | **0,9832** |
| Random Forest — Test | 0,9776 | 0,9957 | 0,9074 | 0,9495 |

Random Forest là **ứng viên tốt nhất trong thực nghiệm theo F1 Validation**.
Trên Test, mô hình phát hiện đúng 14.216 URL phishing và bỏ sót 1.450; có 61
URL hợp pháp bị báo nhầm. Vì Recall giảm từ 0,9706 trên Validation xuống
0,9074 trên Test. API hiện đã được cấu hình dùng Random Forest. Nhóm cần khởi
động lại Backend trước khi demo và nói rõ Recall Test vẫn thấp hơn Validation.

## Giải thích nhanh các chỉ số

- **Accuracy:** tỷ lệ dự đoán đúng trên toàn bộ URL.
- **Precision phishing:** trong số URL mô hình báo là phishing, có bao nhiêu URL
  thực sự là phishing. Precision cao giúp giảm báo động nhầm.
- **Recall phishing:** trong số URL phishing thật, mô hình tìm ra được bao
  nhiêu. Recall thấp nghĩa là còn bỏ sót URL nguy hiểm.
- **F1:** điểm cân bằng giữa Precision và Recall.
- **Confidence:** xác suất do mô hình trả ra theo lớp phishing; đây không phải
  lời bảo đảm rằng một URL an toàn hay nguy hiểm.

## Điểm học được và hạn chế

- **HTTPS có thể là lối tắt:** chỉ dùng HTTPS, Decision Tree đã đạt F1 0,9732
  trên Validation; bỏ HTTPS khỏi Random Forest làm F1 giảm từ 0,9832 xuống
  0,7664. Điều này cho thấy bộ dữ liệu có tín hiệu HTTPS rất mạnh. Nó không
  chứng minh HTTPS là nguyên nhân duy nhất hay HTTPS đồng nghĩa với an toàn.
- **Nhãn có thể đã cũ:** URL và website đổi trạng thái theo thời gian; nhãn của
  bộ dữ liệu tĩnh có thể không còn phản ánh trạng thái hiện tại.
- **Thiên lệch domain:** dữ liệu có thể đại diện không đều cho domain nổi tiếng
  và domain ít gặp. Nhóm chưa đo riêng mức thiên lệch này; cần đánh giá thêm
  trên domain và dữ liệu mới.
- **Phạm vi hệ thống:** mô hình chỉ phân tích chuỗi URL; không tải trang, không
  đọc HTML và không kiểm tra website theo thời gian thực.

## Kịch bản demo ngắn

1. Mở giao diện Streamlit và cho xem ô nhập URL.
2. Dùng một URL hợp pháp và một URL phishing đã được nhóm kiểm tra trước. Chỉ
   nhập URL vào ứng dụng; không mở trang phishing trong trình duyệt.
3. Giải thích nhãn dự đoán, confidence và một vài đặc trưng URL hiển thị.
4. Nhập URL sai định dạng để minh họa kiểm tra đầu vào.
5. Nếu còn thời gian, mở `/docs` hoặc trang MLflow để cho thấy API và nhật ký
   thực nghiệm.

**Chuẩn bị trước buổi giới thiệu:** thử lại đúng URL demo trên máy trình bày và
ghi lại kết quả thực tế; kiểm tra `GET /health` báo mô hình đã nạp. Database
MLflow hiện nằm cục bộ trong `mlflow.db`, nên cần có tệp đó trên máy nếu nhóm
muốn mở giao diện MLflow.

## Câu hỏi có thể được hỏi

**Vì sao chia theo hostname?**

Để hạn chế cùng một hostname xuất hiện ở cả Train và Test, làm điểm đánh giá
phản ánh tốt hơn khả năng gặp domain chưa thấy.

**Vì sao không chỉ dùng Accuracy?**

Dữ liệu lệch lớp và bỏ sót phishing gây rủi ro. Precision, Recall và F1 cho
biết mô hình báo nhầm và bỏ sót ra sao.

**Vì sao API chưa dùng Random Forest?**

Random Forest tốt nhất trên Validation nhưng Recall giảm trên Test. Nhóm chưa
muốn đổi mô hình phục vụ API trước khi hiểu rõ sự chênh lệch này.

**Nếu confidence thấp thì URL chắc chắn an toàn không?**

Không. Đó chỉ là đầu ra của mô hình theo dữ liệu và đặc trưng hiện có; người
dùng vẫn cần thận trọng.
