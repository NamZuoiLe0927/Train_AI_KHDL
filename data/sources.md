# Nguồn dữ liệu Tsinghua University (Nivel-2 Crawling — Đa nguồn)

Ghi nhận từ yêu cầu thu thập dữ liệu AI cho TrainAI.

---

## 1. Cổng thông tin chính thức & Tin tức
- Tsinghua English Portal: https://www.tsinghua.edu.cn/en/
- Tsinghua Facts & Figures: https://www.tsinghua.edu.cn/en/AboutTsinghua/Overview.htm
- Tsinghua News Center: https://www.tsinghua.edu.cn/en/News.htm

## 2. Cơ sở dữ liệu Nghiên cứu & Thư viện
- Tsinghua University Library: https://lib.tsinghua.edu.cn/
- Tsinghua Research Data Services: https://data.tsinghua.edu.cn/ (tương đương)
- Tsinghua Research Feature: https://www.tsinghua.edu.cn/en/Research.htm

## 3. Tuyển sinh & Chương trình Đào tạo
- International Undergraduate Admissions
- Tsinghua Graduate Programs
- Học bổng (tham khảo): HannahEd / các bài hướng dẫn

## 4. Xếp hạng & Chỉ số Quốc tế
- QS World University Rankings (Profile Tsinghua)
- Times Higher Education (THE Profile)
- ARWU / ShanghaiRanking (Profile Tsinghua)

## 5. Bài báo Khoa học & Công nghệ nổi bật
- Nature Index — Tsinghua University
- IEEE Xplore (tác giả/đơn vị Tsinghua)
- ACM Digital Library (AI / Computer Science)

---

## Kỹ thuật thu thập (Scraping Rules — Đã ghi nhớ)
1. Kiểm tra `https://www.tsinghua.edu.cn/robots.txt` trước khi crawl.
2. Trang tiếng Trung (`tsinghua.edu.cn`) chứa dữ liệu đầy đủ hơn trang tiếng Anh (`/en/`).
3. Ưu tiên API học thuật (`OpenAlex`, `Semantic Scholar`) thay vì cào HTML trực tiếp.
4. Dùng `institution.id` của Tsinghua trên OpenAlex để lọc bài báo.

---

## Trạng thái Pipeline
- Nivel-2 Crawling (OpenAlex API): **đang chạy nền** (background)
- Nguồn chính thức trên: **đã ghi nhận** — chờ tích hợp sau khi crawl xong
