# Kiểm tra định dạng thu thập — Promt.txt / Nivel-2

## Định dạng dữ liệu yêu cầu (từ promt.txt)

### 1. Thông tin trường (University Info)
- university_name | chinese_name | founded_year | country | city | description | faculties
- **Status:** Cần thêm file `data/university_info.csv` sau khi crawl official portal

### 2. Nhóm nghiên cứu AI (Research Groups)
- research_group_id | name | department | research_area | website | researchers | projects
- **Status:** Cần crawl `Research Feature` + `Library`

### 3. Nhà nghiên cứu (Researchers)
- researcher_id | name | position | department | research_area | orcid | google_scholar | paper_count | citation_count
- **Status:** Lấy từ OpenAlex + Tsinghua official pages

### 4. Công bố khoa học (Papers — 2015→nay, AI/NLP/LLM)
- paper_id | title | authors | year | month | research_area | subfield | keywords | venue | citation_count | doi | url
- **Status:** Đang crawl OpenAlex (nivel-2). Cần lọc thêm từ `Nature Index`, `IEEE/ACM`.

### 5. NLP Nghiên cứu (NLP Papers)
- paper_id | title | year | authors | nlp_task | language | model | dataset | benchmark | venue | citation_count
- **Status:** Tạo từ dữ liệu papers + phân loại concept_group (NLP)

### 6. LLM / Model
- model_name | organization | release_year | model_type | parameter_count | language | open_source | github_url | paper_url
- **Status:** Cần crawl thêm từ project pages / GitHub

### 7. Dataset / Open Source
- project_id | name | type | description | research_group | year | license | github_url | paper_url | dataset_url
- **Status:** Từ `Tsinghua Research Data Services`

### 8. Thống kê theo năm (Yearly Stats)
- year | total_papers | ai_papers | nlp_papers | llm_papers | citation_count | open_source_projects | researchers_count
- **Status:** Tạo từ feature engineering (đã có code)

---

## Checklist sẵn sàng chạy (cbi chạy)

- [x] Folder cấu trúc (data/raw, processed, final, notebooks, outputs, reports, src)
- [x] Config cập nhật (OpenAlex + 5 nguồn chính thức Tsinghua)
- [x] Scraper (OpenAlex API đa trang — nivel-2 crawl)
- [x] Cleaner (json_normalize, ép kiểu, drop dup, feature cơ bản)
- [x] Feature Engineering (paper_age, citation_level, concept_group, is_top_venue...)
- [x] Visualization (9 static PNG + 3 interactive HTML + dashboard)
- [x] Notebook EDA (`notebooks/analysis.ipynb`)
- [x] Source docs (`data/sources.md`)
- [x] Scraping rules ghi nhó (robots, tiếng Trung, ưu tiên API)
- [ ] **Crawling đang chạy nền (OpenAlex)** — chờ xong để có `data/raw/openalex_raw.json`
- [ ] **Crawling nguồn chính thức** — cần thêm module cho Tsinghua portals (sau khi crawl API xong)
- [ ] Xuất CSV/JSON/Parquet theo danh sách trên (`university_info.csv`, `papers.csv`, v.v.)

---

## Lưu ý kỹ thuật khi chạy
1. Chạy `python src/main.py` từ thư mục `TrainAI/` (đã test lần 1, cần thời gian crawl dài)
2. Nếu crawl quá lâu, có thể dừng và dùng `data/raw/openalex_raw.json` mẫu để đi tiếp bước 4-6
3. Sau khi có raw data, chạy lần lượt: `clean.py` → `features.py` → `visualize.py`
4. Để lấy bài báo Tsinghua chính xác hơn: dùng OpenAlex filter `institution.id:I4210120001` (cần xác minh ID chính xác)
