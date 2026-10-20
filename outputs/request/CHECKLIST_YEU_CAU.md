# Kết quả đối chiếu yêu cầu — TrainAI

| Yêu cầu | Trạng thái | Kết quả |
|---|---|---|
| Thu thập bằng API mở | Đạt | OpenAlex Works API qua `requests`; affiliation Tsinghua `I99065089`, topic AI subfield `1702` |
| Phạm vi thời gian | Đạt | 2015-01-01 đến 2026-10-08; 2026 là năm chưa trọn vẹn |
| Mẫu dữ liệu | Đạt có giới hạn | 1.200/32.357 công trình; quota phân bổ tỷ lệ theo năm, tối đa 200/năm, không phải mẫu ngẫu nhiên |
| Chuẩn hóa và làm sạch | Đạt | 1.200 hàng, 63 cột sau clean; nested OpenAlex metadata được giữ có cấu trúc, trùng theo ID được loại |
| Đặc trưng dẫn xuất | Đạt | Nhóm lĩnh vực, trích dẫn/năm, tuổi bài, mức hợp tác, độ dài abstract và trường thời gian |
| Histogram / Boxplot / Violin | Đạt | `outputs/figures/` |
| Line / Area theo thời gian | Đạt | `outputs/figures/`; đọc như phân bố của mẫu có quota |
| Scatter + hồi quy | Đạt | `outputs/figures/scatter_year_vs_citations.png` |
| Heatmap tương quan | Đạt | `outputs/figures/heatmap_correlation.png` |
| Treemap / Sunburst hoặc bản đồ | Đạt | Treemap Plotly tương tác; không tự tạo tọa độ địa lý |
| WordCloud và Network graph | Đạt | Từ tiêu đề bài báo và metadata authorship OpenAlex |
| Tối thiểu 3 biểu đồ tương tác | Đạt | 3 biểu đồ Plotly và dashboard tổng hợp |
| Storytelling một trang | Đạt | `Storytelling_bao_cao.html`; số liệu và giới hạn lấy trực tiếp từ bộ dữ liệu mới |
| CSV / JSON / Parquet | Đạt một phần | Raw JSON, clean/final Parquet, CSV papers/researchers/yearly stats/data dictionary |
| Báo cáo chất lượng dữ liệu | Đạt | Missing values, trùng ID, DOI, kiểm tra affiliation/topic và giới hạn mẫu |
| Nhóm nghiên cứu / LLM / datasets / projects / rankings | Chưa thu thập | CSV đúng schema được tạo nhưng để trống; cần nguồn chính thức hoặc nguồn xác minh riêng |

## Kết quả xác minh dữ liệu

- OpenAlex báo 32.357 công trình khớp truy vấn trong phạm vi ngày.
- Bộ dữ liệu lưu 1.200 bài, từ năm 2015 đến 2026; 1.200/1.200 có topic AI subfield hiển thị.
- 1.197/1.200 raw records hiển thị ID Tsinghua trong authorships; ba bản ghi còn lại vẫn khớp bộ lọc API nhưng metadata affiliation trả về không hiển thị ID đó.
- Dữ liệu sau làm sạch có 1.200 hàng, 63 cột; dữ liệu cuối có 72 cột và không có ID trùng.
- Venue được lấy từ `primary_location.source`; abstract được đếm từ inverted index khi có dữ liệu. Giá trị thiếu không được thay bằng dữ liệu suy đoán.
- OpenAlex affiliation/topic và trích dẫn chưa được đối chiếu độc lập với toàn văn hoặc hệ thống xuất bản.

## Đầu ra chính

- Dữ liệu: `data/raw/`, `data/processed/`, `data/final/`
- Biểu đồ: `outputs/figures/`
- Dashboard và báo cáo: `outputs/reports/`
