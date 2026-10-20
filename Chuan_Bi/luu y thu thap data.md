# CẨM NANG THU TẬP DỮ LIỆU (DATA COLLECTION GUIDE)

> **Triết lý cốt lõi:** Quy trình thu thập dữ liệu hiệu quả không nằm ở việc "càng nhiều càng tốt", mà dựa trên 5 trụ cột: **Đúng nhu cầu - Đúng pháp lý - Chất lượng cao - Hạ tầng ổn định - Chi phí tối ưu**.

---

## 1. Các Phương Pháp Thu Tập Dữ Liệu Phổ Biến

Tùy vào định dạng và vị trí nguồn dữ liệu, phương pháp thu thập sẽ được chia thành các nhóm chính:

| Phương pháp | Mô tả | Trường hợp sử dụng | Ưu / Nhược điểm |
| :--- | :--- | :--- | :--- |
| **API Integration** | Lấy dữ liệu qua các cổng RESTful API, GraphQL do bên cung cấp mở sẵn. | Dữ liệu từ Facebook, Google, CRM, ERP, Hệ thống tài chính. | **+** An toàn, ổn định, đúng chuẩn.<br>**-** Bị giới hạn lượt gọi (Rate limit), có thể tính phí. |
| **Web Scraping / Crawling** | Tự động hóa trình duyệt hoặc gửi HTTP request để lấy dữ liệu từ HTML trang web. | Lấy giá sản phẩm thương mại điện tử, tin tức, bất động sản. | **+** Thu thập được dữ liệu công khai không có API.<br>**-** Dễ bị chặn IP, dễ hỏng code khi web đổi giao diện. |
| **Database & Event Logs** | Trích xuất từ CSDL nội bộ qua SQL, Change Data Capture (CDC), hoặc Event Tracking. | Theo dõi hành vi người dùng (App/Web log), giao dịch bán hàng. | **+** Dữ liệu chuẩn xác, thời gian thực.<br>**-** Cần phân quyền chặt chẽ, tránh gây tải cho CSDL sản xuất. |
| **Streaming / IoT** | Thu thập dữ liệu liên tục theo thời gian thực từ cảm biến, thiết bị thông minh. | Hệ thống xe tự lái, cảm biến nhà máy, theo dõi nhịp tim. | **+** Độ trễ cực thấp.<br>**-** Hạ tầng xử lý phức tạp (Kafka, MQTT). |
| **Data thứ cấp & Khảo sát** | Tải các bộ dữ liệu sẵn có (Dataset) hoặc thu thập qua biểu mẫu. | Nghiên cứu thị trường, huấn luyện mô hình AI ban đầu. | **+** Nhanh chóng, tốn ít chi phí kỹ thuật.<br>**-** Độ tùy biến không cao. |

---

## 2. 4 "Cái Bẫy" Cần Chú Ý Khi Thu Tập Dữ Liệu

### 2.1. Bẫy Pháp Lý & Đạo Đức (Bắt buộc kiểm tra trước)
* **Quyền riêng tư (Data Privacy Laws):** Tuân thủ **Nghị định 13/2023/NĐ-CP** (Việt Nam), **GDPR** (Châu Âu) hoặc **CCPA** (Mỹ). 
  * *Lưu ý:* Tuyệt đối không tự ý thu thập **Thông tin Định danh Cá nhân (PII)** như CCCD, SĐT, Email, Số tài khoản ngân hàng khi chưa có sự đồng ý (Consent) của chủ thể.
* **Điều khoản dịch vụ (Terms of Service - ToS):** Nhiều trang web cấm hành vi tự động thu thập dữ liệu trong điều khoản sử dụng.
* **Tệp `robots.txt`:** Kiểm tra đường dẫn `domain.com/robots.txt` trước khi cào dữ liệu để biết các đường dẫn bị cấm (`Disallow`).

### 2.2. Bẫy Kỹ Thuật & Cơ Chế Chống Cào (Anti-Scraping)
Khi cào dữ liệu từ các hệ thống lớn, bạn sẽ gặp các rào cản kỹ thuật:
* **Rate Limiting & IP Blocking:** Máy chủ sẽ khóa IP nếu nhận quá nhiều request trong thời gian ngắn.
  * *Giải pháp:* Thêm độ trễ ngẫu nhiên (`time.sleep`), sử dụng cơ chế xoay vòng IP (Proxy Rotation).
* **CAPTCHA & Cloudflare/Akamai Protection:**
  * *Giải pháp:* Dùng Headless Browser (`Playwright`, `Puppeteer`), dịch vụ giải CAPTCHA hoặc giả lập thông số trình duyệt thật (`User-Agent`, `Headers`, `Cookies`).
* **Giao diện thay đổi (Schema Drift):** Website thay đổi cấu trúc HTML/CSS làm hỏng đoạn code cào dữ liệu.
  * *Giải pháp:* Xây dựng hệ thống cảnh báo (Alerting) khi dữ liệu trả về bị rỗng hoặc rác.

### 2.3. Bẫy Chất Lượng Dữ Liệu (*"Garbage In, Garbage Out"*)
Đánh giá chất lượng dữ liệu đầu vào theo 5 tiêu chí chuẩn:
1. **Accuracy (Tính chính xác):** Dữ liệu có phản ánh đúng thực tế không?
2. **Completeness (Tính đầy đủ):** Có bị khuyết/thiếu các trường dữ liệu quan trọng (`Null`/`Missing`) không?
3. **Consistency (Tính nhất quán):** Định dạng ngày tháng, đơn vị tiền tệ, bảng mã tiếng Việt (`UTF-8`) có đồng nhất không?
4. **Uniqueness (Tính duy nhất):** Có bị trùng lặp bản ghi (Duplicate Data) không?
5. **Timeliness (Tính cập nhật):** Dữ liệu có còn đúng ở thời điểm hiện tại không?

### 2.4. Bẫy Chi Phí & Hạ Tầng Lưu Trữ
* **Tốn dung lượng thừa:** Thu thập cả những trường dữ liệu không bao giờ dùng tới (HTML thừa, file ảnh rác) làm phình to Data Lake/Database.
* **Độ lặp lại (Idempotency):** Tiến trình thu thập phải đảm bảo nếu bị gián đoạn và chạy lại, dữ liệu sẽ **không** bị ghi trùng (Duplicate Key) hay làm sai lệch dữ liệu cũ.

---

## 3. Quy Trình Chuẩn Của Chuyên Gia Thu Tập Dữ Liệu

```
[1. Xác định mục tiêu] 
       │
       ▼
[2. Khảo sát nguồn dữ liệu] 
       │
       ▼
[3. Xác minh Pháp lý & ToS] 
       │
       ▼
[4. Thiết kế Pipeline (ETL/ELT)] 
       │
       ▼
[5. Lưu trữ Dữ liệu Thô (Raw Data)] 
       │
       ▼
[6. Làm sạch & Biến đổi (Clean & Transform)]
```

---

## 4. Các Nguyên Tắc Vàng (Best Practices)

1. **Luôn lưu trữ Dữ liệu Gốc (Raw Data):** Trước khi làm sạch hay biến đổi, hãy lưu bản sao gốc vào Data Lake (S3, MinIO, Google Cloud Storage) dưới dạng file `.json`, `.parquet` hoặc `.csv`. Nếu logic biến đổi bị lỗi, bạn vẫn còn bản gốc để xử lý lại mà không phải cào lại từ đầu.
2. **Xây dựng cơ hệ giám sát (Logging & Monitoring):** Mỗi tiến trình thu thập phải ghi nhận chi tiết:
   * Số bản ghi lấy thành công / thất bại.
   * Thời gian phản hồi của server (Response time).
   * Mã lỗi HTTP (`403 Forbidden`, `429 Too Many Requests`, `500 Server Error`...).
3. **Thu thập tăng tiến (Incremental Extraction):** Chỉ lấy các bản ghi mới hoặc có sự thay đổi kể từ lần cào cuối cùng, tránh tải lại toàn bộ hệ thống (Full Dump) gây tốn tài nguyên.