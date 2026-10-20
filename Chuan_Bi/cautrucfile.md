# CẨM NANG TRIỂN KHAI HOÀN CHỈNH: THU THẬP – CHUẨN HÓA – TRỰC QUAN HÓA DỮ LIỆU

> **Triết lý cốt lõi:** Quy trình thu thập dữ liệu hiệu quả không nằm ở việc "càng nhiều càng tốt", mà dựa trên 5 trụ cột: **Đúng nhu cầu – Đúng pháp lý – Chất lượng cao – Hạ tầng ổn định – Chi phí tối ưu**.

> **Mục tiêu bài toán:** Xây dựng pipeline hoàn chỉnh: thu thập bằng `requests/BeautifulSoup` hoặc API mở → chuẩn hóa kiểu dữ liệu → xử lý thiếu → tạo cột đặc trưng → trực quan hóa đủ 6 nhóm biểu đồ → có **ít nhất 3 biểu đồ tương tác** (Plotly/Altair/Bokeh).

---

## MỤC LỤC

1. [Tổng quan & chọn nguồn dữ liệu](#phần-1--tổng-quan--chọn-nguồn-dữ-liệu)
2. [Cấu trúc thư mục & cấu hình](#phần-2--cấu-trúc-thư-mục--cấu-hình)
3. [4 "cái bẫy" cần chú ý](#phần-3--4-cái-bẫy-cần-chú-ý-khi-thu-tập-dữ-liệu)
4. [Pipeline 6 bước](#phần-4--pipeline-6-bước)
5. [Nguyên tắc vàng (Best Practices)](#phần-5--nguyên-tắc-vàng-best-practices)
6. [Checklist pháp lý – chất lượng – hạ tầng](#phần-6--checklist-pháp-lý--chất-lượng--hạ-tầng)
7. [Kết quả đầu ra tối thiểu](#phần-7--kết-quả-đầu-ra-tối-thiểu)
8. [Quy trình chuẩn của chuyên gia](#phần-8--quy-trình-chuẩn-của-chuyên-gia-thu-tập-dữ-liệu)
9. [Phụ lục — Lưu ý tổng hợp](#phụ-lục--lưu-ý-tổng-hợp)

---

## PHẦN 1 — TỔNG QUAN & CHỌN NGUỒN DỮ LIỆU

### 1.1. Các phương pháp thu thập dữ liệu phổ biến

| Phương pháp | Mô tả | Trường hợp sử dụng | Ưu / Nhược điểm |
| :--- | :--- | :--- | :--- |
| **API Integration** | Lấy dữ liệu qua RESTful API, GraphQL do bên cung cấp mở sẵn. | Facebook, Google, CRM, ERP, tài chính. | **+** An toàn, ổn định, đúng chuẩn.<br>**-** Giới hạn lượt gọi (Rate limit), có thể tính phí. |
| **Web Scraping / Crawling** | Tự động hóa trình duyệt hoặc gửi HTTP request lấy dữ liệu HTML. | Giá sản phẩm TMĐT, tin tức, bất động sản. | **+** Lấy được dữ liệu công khai không có API.<br>**-** Dễ bị chặn IP, dễ hỏng khi web đổi giao diện. |
| **Database & Event Logs** | Trích xuất từ CSDL nội bộ qua SQL, CDC, Event Tracking. | Hành vi người dùng (App/Web log), giao dịch bán hàng. | **+** Chuẩn xác, thời gian thực.<br>**-** Cần phân quyền, tránh tải CSDL sản xuất. |
| **Streaming / IoT** | Thu thập liên tục theo thời gian thực từ cảm biến, thiết bị thông minh. | Xe tự lái, cảm biến nhà máy, nhịp tim. | **+** Độ trễ cực thấp.<br>**-** Hạ tầng phức tạp (Kafka, MQTT). |
| **Data thứ cấp & Khảo sát** | Tải Dataset sẵn có hoặc thu thập qua biểu mẫu. | Nghiên cứu thị trường, huấn luyện AI ban đầu. | **+** Nhanh, ít chi phí kỹ thuật.<br>**-** Độ tùy biến không cao. |

### 1.2. Nguồn đề xuất: OpenAlex API

Chọn **OpenAlex** (`https://api.openalex.org/works`) vì:
- Không cần API key.
- Có thời gian xuất bản → vẽ **Line/Area**.
- Có quốc gia, tổ chức → vẽ **Map (Choropleth)**.
- Có abstract, concept → vẽ **WordCloud, Treemap**.
- Có tác giả, đồng tác giả → vẽ **Network graph**.
- Có citation, năm, số lượng tác giả → vẽ **Histogram, Scatter, Heatmap**.

*(Có thể thay bằng `books.toscrape.com` nếu muốn demo scraping, nhưng khó có đủ dữ liệu thời gian/bản đồ.)*

---

## PHẦN 2 — CẤU TRÚC THƯ MỤC & CẤU HÌNH

### 2.1. Cấu trúc thư mục

```text
project/
├── config/
│   └── config.yaml
├── data/
│   ├── raw/
│   │   └── openalex_raw.json
│   └── processed/
│       └── openalex_clean.parquet
├── notebooks/
│   └── analysis.ipynb
├── src/
│   ├── extract.py
│   ├── clean.py
│   ├── features.py
│   └── visualize.py
├── outputs/
│   ├── figures/
│   └── dashboard.html
├── requirements.txt
└── README.md

requirements.txt :

requests
beautifulsoup4
lxml
pandas
numpy
pyarrow
matplotlib
seaborn
plotly
folium
wordcloud
networkx
scikit-learn
statsmodels
jupyter
pyyaml


config/config.yaml : 

source:
  type: "api"          # api | scraping
  name: "openalex"
  base_url: "https://api.openalex.org/works"
  params:
    filter: "from_publication_date:2020-01-01,to_publication_date:2024-12-31"
    per-page: 200
    cursor: "*"
  headers:
    User-Agent: "StudentDataProject/1.0 (mailto:your_email@example.com)"
  timeout: 30
  max_retries: 3
  delay_seconds: 1

storage:
  raw_path: "data/raw/openalex_raw.json"
  processed_path: "data/processed/openalex_clean.parquet"
  figure_dir: "outputs/figures"
  dashboard_path: "outputs/dashboard.html"

legal:
  check_robots_txt: true
  check_tos: true
  allow_pii: false
  note: "Chỉ dùng API mở, không thu thập PII, tuân thủ rate limit."


chú ý 

4 "CÁI BẪY" CẦN CHÚ Ý KHI THU TẬP DỮ LIỆU
3.1. Bẫy Pháp Lý & Đạo Đức (bắt buộc kiểm tra trước)
Quyền riêng tư (Data Privacy Laws): Tuân thủ Nghị định 13/2023/NĐ-CP (Việt Nam), GDPR (EU), CCPA (Mỹ).

Lưu ý: Tuyệt đối không tự ý thu thập Thông tin Định danh Cá nhân (PII) như CCCD, SĐT, Email, Số tài khoản ngân hàng khi chưa có sự đồng ý (Consent).

Điều khoản dịch vụ (Terms of Service – ToS): Nhiều trang web cấm hành vi thu thập tự động trong điều khoản sử dụng.

Tệp robots.txt: Kiểm tra domain.com/robots.txt trước khi cào để biết đường dẫn bị cấm (Disallow).

3.2. Bẫy Kỹ Thuật & Cơ Chế Chống Cào (Anti-Scraping)
Rate Limiting & IP Blocking: Máy chủ khóa IP nếu có quá nhiều request trong thời gian ngắn.

Giải pháp: Thêm độ trễ ngẫu nhiên (time.sleep), sử dụng Proxy Rotation.

CAPTCHA & Cloudflare/Akamai Protection:

Giải pháp: Dùng Headless Browser (Playwright, Puppeteer), dịch vụ giải CAPTCHA, giả lập User-Agent, Headers, Cookies.

Giao diện thay đổi (Schema Drift): Website thay đổi HTML/CSS làm hỏng code.

Giải pháp: Xây dựng hệ thống cảnh báo (Alerting) khi dữ liệu rỗng hoặc rác.

3.3. Bẫy Chất Lượng Dữ Liệu ("Garbage In, Garbage Out")
Đánh giá chất lượng theo 5 tiêu chí:

Accuracy (Tính chính xác): Dữ liệu có phản ánh đúng thực tế?

Completeness (Tính đầy đủ): Có bị khuyết/thiếu trường quan trọng (Null/Missing)?

Consistency (Tính nhất quán): Định dạng ngày tháng, đơn vị tiền tệ, bảng mã tiếng Việt (UTF-8) có đồng nhất?

Uniqueness (Tính duy nhất): Có bị trùng lặp bản ghi (Duplicate Data)?

Timeliness (Tính cập nhật): Dữ liệu có còn đúng ở thời điểm hiện tại?

3.4. Bẫy Chi Phí & Hạ Tầng Lưu Trữ
Tốn dung lượng thừa: Thu thập cả trường không bao giờ dùng (HTML thừa, ảnh rác) làm phình to Data Lake/Database.

Độ lặp lại (Idempotency): Tiến trình phải đảm bảo nếu bị gián đoạn và chạy lại, dữ liệu không bị ghi trùng (Duplicate Key) hay sai lệch dữ liệu cũ.


PIPELINE 6 BƯỚC :

[1. Thu thập dữ liệu] 
       │
       ▼
[2. Chuẩn hóa & làm sạch] 
       │
       ▼
[3. Tạo cột đặc trưng mới] 
       │
       ▼
[4. Lưu dữ liệu sạch] 
       │
       ▼
[5. Trực quan hóa] 
       │
       ▼
[6. Xuất dashboard tương tác]


Chuẩn hóa : 


Bước 1 — Thu thập dữ liệu
Mục tiêu: Lấy dữ liệu thô từ nguồn hợp pháp, lưu lại bản gốc.

Cách làm:

Dùng requests/BeautifulSoup hoặc API mở.

Kiểm tra robots.txt, ToS nếu scraping.

Tuân thủ rate limit, thêm time.sleep() ngẫu nhiên.

Lưu raw data dưới dạng .json, .csv hoặc .parquet.

python
import requests, json, time
from pathlib import Path

def fetch_openalex(config):
    url = config["source"]["base_url"]
    params = config["source"]["params"].copy()
    headers = config["source"]["headers"]
    results = []

    while True:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        params["cursor"] = cursor
        time.sleep(1)

    Path(config["storage"]["raw_path"]).parent.mkdir(parents=True, exist_ok=True)
    with open(config["storage"]["raw_path"], "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    return results
Bước 2 — Chuẩn hóa & làm sạch dữ liệu
Mục tiêu: Chuyển dữ liệu thô thành DataFrame sạch, đúng kiểu, xử lý thiếu và trùng lặp.

Cách làm:

Chuyển JSON → DataFrame.

Ép kiểu: ngày tháng, số, phân loại, văn bản.

Xử lý thiếu: dropna, fill median/mode, hoặc đánh dấu is_missing.

Loại trùng theo id/doi.

Chuẩn hóa UTF-8, đơn vị, định dạng ngày.

python
import pandas as pd

def clean_data(raw):
    df = pd.json_normalize(raw)
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
    df["publication_year"] = df["publication_date"].dt.year
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0)
    df = df.drop_duplicates(subset=["id"])
    return df
Bước 3 — Tạo cột đặc trưng mới
Mục tiêu: Bổ sung các biến phái sinh phục vụ phân tích và trực quan hóa.

Cách làm:

Thời gian: year, month, quarter, age.

Đếm: authors_count, concepts_count, countries_count.

Text: abstract_length, title_length, is_international.

Phân nhóm: citation_level, concept_group.

python
df["authors_count"] = df["authorships"].apply(lambda x: len(x) if isinstance(x, list) else 0)
df["is_international"] = df["authorships"].apply(
    lambda x: len({a.get("countries", [None])[0] for a in x if a.get("countries")}) > 1
)
df["abstract_length"] = df["abstract_inverted_index"].apply(
    lambda x: len(x) if isinstance(x, dict) else 0
)
Bước 4 — Lưu dữ liệu sạch
Mục tiêu: Lưu trữ dữ liệu đã xử lý để tái sử dụng, đảm bảo idempotency.

Cách làm:

Lưu parquet để đọc nhanh, giữ kiểu dữ liệu.

Lưu thêm .csv nếu cần mở bằng Excel.

Đảm bảo chạy lại không ghi trùng.

python
df.to_parquet("data/processed/openalex_clean.parquet", index=False)
df.to_csv("data/processed/openalex_clean.csv", index=False, encoding="utf-8-sig")
Bước 5 — Trực quan hóa dữ liệu
Mục tiêu: Biểu diễn dữ liệu đủ 6 nhóm biểu đồ theo yêu cầu.

Yêu cầu	Cách làm	Thư viện
Histogram/Boxplot/Violin	Phân phối cited_by_count, authors_count	plotly.express
Line/Area theo thời gian	Số bài báo theo năm/quý	plotly.express
Scatter + hồi quy	publication_year vs cited_by_count	plotly.express + trendline="ols"
Heatmap tương quan	Ma trận tương quan các biến số	plotly.express.imshow
Treemap/Sunburst hoặc Bản đồ	Concept theo nhóm; bản đồ quốc gia	plotly.express.treemap, choropleth
WordCloud hoặc Network	WordCloud abstract; Network đồng tác giả	wordcloud, networkx
python
import plotly.express as px

fig1 = px.histogram(df, x="cited_by_count", nbins=50, title="Phân phối trích dẫn")
fig2 = px.line(df.groupby("publication_year").size().reset_index(name="count"),
               x="publication_year", y="count", title="Số bài báo theo năm")
fig3 = px.scatter(df, x="publication_year", y="cited_by_count",
                  trendline="ols", title="Năm xuất bản vs Trích dẫn")
Bước 6 — Xuất dashboard tương tác
Mục tiêu: Gộp các biểu đồ tương tác vào một file HTML duy nhất.

Cách làm:

Dùng Plotly/Altair/Bokeh.

Ít nhất 3 biểu đồ tương tác: Histogram, Line, Scatter, Treemap, Choropleth.

Xuất file dashboard.html.

python
with open("outputs/dashboard.html", "w", encoding="utf-8") as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs="cdn"))
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write(fig3.to_html(full_html=False, include_plotlyjs=False))



NGUYÊN TẮC VÀNG (BEST PRACTICES)
Luôn lưu trữ Dữ liệu Gốc (Raw Data): Trước khi làm sạch hay biến đổi, lưu bản gốc vào Data Lake (S3, MinIO, GCS) dưới dạng .json, .parquet hoặc .csv. Nếu logic biến đổi lỗi, vẫn còn bản gốc để xử lý lại mà không phải cào lại từ đầu.

Xây dựng hệ thống giám sát (Logging & Monitoring): Mỗi tiến trình thu thập phải ghi nhận chi tiết:

Số bản ghi lấy thành công / thất bại.

Thời gian phản hồi của server (Response time).

Mã lỗi HTTP (403 Forbidden, 429 Too Many Requests, 500 Server Error...).

Thu thập tăng tiến (Incremental Extraction): Chỉ lấy bản ghi mới hoặc có thay đổi kể từ lần cào cuối, tránh Full Dump gây tốn tài nguyên.


PHẦN 6 — CHECKLIST PHÁP LÝ – CHẤT LƯỢNG – HẠ TẦNG
□ Kiểm tra robots.txt và ToS nếu scraping.
□ Không thu thập PII khi chưa có consent.
□ Tuân thủ rate limit, thêm delay/proxy nếu cần.
□ Lưu raw data trước khi làm sạch.
□ Ghi log: số bản ghi thành công/thất bại, HTTP status, response time.
□ Thu thập tăng tiến: chỉ lấy bản ghi mới/thay đổi.
□ Kiểm tra 5 tiêu chí chất lượng: Accuracy, Completeness, Consistency, Uniqueness, Timeliness.
□ Đảm bảo idempotency: chạy lại không ghi trùng.
PHẦN 7 — KẾT QUẢ ĐẦU RA TỐI THIỂU
data/raw/openalex_raw.json — dữ liệu gốc.

data/processed/openalex_clean.parquet — dữ liệu sạch, có feature mới.

notebooks/analysis.ipynb — phân tích & biểu đồ.

outputs/dashboard.html — ít nhất 3 biểu đồ tương tác.

outputs/figures/ — đủ 6 nhóm biểu đồ.

QUY TRÌNH CHUẨN CỦA CHUYÊN GIA THU TẬP DỮ LIỆU
text
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



PHỤ LỤC — LƯU Ý TỔNG HỢP
Luôn đọc kỹ tài liệu API trước khi gọi để tránh vượt rate limit.

Với scraping, luôn kiểm tra robots.txt, ToS và cân nhắc dùng API chính thức nếu có.

Không lưu PII dưới bất kỳ hình thức nào nếu chưa có consent bằng văn bản.

Đặt tên cột rõ ràng, thống nhất snake_case để dễ xử lý.

Luôn kiểm tra dữ liệu sau mỗi bước: shape, dtype, missing, duplicate.

Xuất biểu đồ ra cả PNG (báo cáo tĩnh) và HTML (tương tác).

Ghi log mọi lần chạy pipeline để dễ debug và tái lập.

Commit code + config + requirements lên Git để đảm bảo khả năng tái lập.
