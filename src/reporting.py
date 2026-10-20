"""Export analysis tables and data-backed HTML reports."""

import html
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


STATIC_CHARTS = [
    ("histogram_citations.png", "Histogram lượt trích dẫn"),
    ("boxplot_citations_by_area.png", "Boxplot lượt trích dẫn theo lĩnh vực"),
    ("violin_citations_venue.png", "Violin plot theo nhóm venue"),
    ("line_papers_per_year.png", "Số bài báo theo năm"),
    ("area_papers_by_area.png", "Diễn biến lĩnh vực theo năm"),
    ("scatter_year_vs_citations.png", "Scatter và hồi quy năm–trích dẫn"),
    ("heatmap_correlation.png", "Heatmap tương quan"),
    ("treemap_concept_groups.png", "Phân bố lĩnh vực nghiên cứu"),
    ("wordcloud_titles.png", "Word cloud tiêu đề"),
    ("network_coauthors.png", "Mạng lưới đồng tác giả"),
]


def create_reports(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """Write CSV exports, a data-quality report, and the research storytelling page."""
    storage = config["storage"]
    reports_dir = Path(storage["dashboard_path"]).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    metadata = _load_collection_metadata(storage["metadata_path"])

    papers = _papers_table(df)
    papers.to_csv(storage["papers_csv_path"], index=False, encoding="utf-8-sig")
    _researchers_table(df).to_csv(
        storage["researchers_csv_path"], index=False, encoding="utf-8-sig"
    )
    _write_empty_source_tables(storage)
    _write_university_info(storage["university_info_csv_path"])
    yearly = _yearly_table(df, metadata)
    yearly.to_csv(storage["yearly_statistics_csv_path"], index=False, encoding="utf-8-sig")
    _data_dictionary(df).to_csv(
        storage["data_dictionary_csv_path"], index=False, encoding="utf-8-sig"
    )
    _write_quality_report(df, metadata, storage["quality_report_path"])
    _write_storytelling_report(
        df, yearly, metadata, storage["storytelling_report_path"]
    )
    _write_storytelling_report(
        df, yearly, metadata, storage["final_report_path"]
    )
    print(f"    Reports and CSV exports saved to {reports_dir}")


def _write_empty_source_tables(storage: Dict[str, Any]) -> None:
    schemas = {
        "research_groups_csv_path": [
            "research_group_id", "name", "department", "research_area",
            "website", "researchers", "projects",
        ],
        "llm_models_csv_path": [
            "model_name", "organization", "release_year", "model_type",
            "parameter_count", "language", "open_source", "github_url", "paper_url",
        ],
        "datasets_csv_path": [
            "project_id", "name", "type", "description", "research_group",
            "year", "license", "github_url", "paper_url", "dataset_url",
        ],
        "open_source_projects_csv_path": [
            "project_id", "name", "description", "research_group",
            "year", "license", "github_url", "paper_url", "dataset_url",
        ],
        "rankings_csv_path": [
            "ranking_name", "year", "rank", "category", "source_url",
        ],
    }
    for config_key, columns in schemas.items():
        pd.DataFrame(columns=columns).to_csv(
            storage[config_key], index=False, encoding="utf-8-sig"
        )


def _write_university_info(output_path: str) -> None:
    profile = pd.DataFrame([{
        "university_name": "Tsinghua University",
        "chinese_name": "清华大学",
        "country": "China",
        "city": "Beijing",
        "founded_year": 1911,
        "official_website": "https://www.tsinghua.edu.cn/",
        "description": "Public research university in Beijing, China.",
        "source_url": "https://www.tsinghua.edu.cn/en/AboutTsinghua/Overview.htm",
    }])
    profile.to_csv(output_path, index=False, encoding="utf-8-sig")


def _load_collection_metadata(metadata_path: str) -> Dict[str, Any]:
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"OpenAlex collection metadata not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _author_values(authorships: Any) -> List[Dict[str, Any]]:
    if not isinstance(authorships, (list, tuple, np.ndarray)):
        return []
    return [
        authorship.get("author", {})
        for authorship in authorships
        if isinstance(authorship, dict) and isinstance(authorship.get("author"), dict)
    ]


def _records(values: Any) -> List[Dict[str, Any]]:
    if not isinstance(values, (list, tuple, np.ndarray)):
        return []
    return [value for value in values if isinstance(value, dict)]


def _join_values(values: Any) -> str:
    if isinstance(values, (list, tuple, np.ndarray)):
        return "; ".join(str(value) for value in values if value)
    return ""


def _papers_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        authors = _author_values(row.get("authorships"))
        location = row.get("primary_location")
        source = (
            location.get("source") or {}
            if isinstance(location, dict) else {}
        )
        rows.append({
            "paper_id": row.get("id"),
            "title": row.get("title"),
            "authors": "; ".join(
                author.get("display_name", "")
                for author in authors if author.get("display_name")
            ),
            "year": row.get("publication_year"),
            "month": row.get("publication_month"),
            "research_area": row.get("primary_topic_name"),
            "subfield": row.get("primary_subfield"),
            "keywords": _join_values(row.get("keyword_names")),
            "venue": row.get("venue_name"),
            "venue_type": source.get("type", ""),
            "journal": "",
            "conference": "",
            "citation_count": row.get("cited_by_count"),
            "institution": "Tsinghua University (OpenAlex affiliation filter)",
            "research_group": "",
            "doi": row.get("doi"),
            "paper_url": (
                location.get("landing_page_url", "")
                if isinstance(location, dict) else ""
            ) or row.get("doi") or row.get("id"),
            "code_url": "",
            "dataset_url": "",
            "source_url": row.get("id"),
            "concept_group": row.get("concept_group"),
        })
    return pd.DataFrame(rows)


def _researchers_table(df: pd.DataFrame) -> pd.DataFrame:
    researcher_rows: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        cited_by_count = int(row.get("cited_by_count", 0) or 0)
        for author in _author_values(row.get("authorships")):
            author_id = author.get("id")
            if not author_id:
                continue
            researcher = researcher_rows.setdefault(author_id, {
                "researcher_id": author_id,
                "name": author.get("display_name", ""),
                "orcid": author.get("orcid", ""),
                "papers_in_sample": 0,
                "citations_of_sampled_papers": 0,
            })
            researcher["papers_in_sample"] += 1
            researcher["citations_of_sampled_papers"] += cited_by_count
    return pd.DataFrame(researcher_rows.values())


def _yearly_table(df: pd.DataFrame, metadata: Dict[str, Any]) -> pd.DataFrame:
    records = []
    for year, row in df.groupby("publication_year", dropna=True):
        year = int(year)
        sampled = row
        sample_info = metadata.get("yearly_counts", {}).get(str(year), {})
        title_text = sampled["title"].fillna("").astype(str)
        llm_mask = title_text.str.contains(
            r"\b(?:LLM|large language model|GPT|ChatGPT|generative language model)\b",
            case=False,
            regex=True,
        )
        records.append({
            "year": year,
            "available_works_openalex": sample_info.get("available"),
            "sampled_papers": len(sampled),
            "ai_papers_in_sample": len(sampled),
            "nlp_papers_in_sample": int((sampled["concept_group"] == "NLP").sum()),
            "llm_title_matches_in_sample": int(llm_mask.sum()),
            "citation_count_in_sample": int(sampled["cited_by_count"].sum()),
            "researchers_in_sample": len({
                author.get("id")
                for authorships in sampled["authorships"]
                for author in _author_values(authorships)
                if author.get("id")
            }),
        })
    return pd.DataFrame(records).sort_values("year")


def _data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    engineered = {
        "paper_age", "citations_per_year", "citation_level", "single_author",
        "large_team", "concept_group", "is_top_venue", "abstract_length",
        "year_month", "countries_count", "is_international",
    }
    descriptions = {
        "id": "OpenAlex work identifier",
        "title": "Publication title",
        "publication_date": "Publication date in OpenAlex",
        "publication_year": "Publication year",
        "publication_month": "Publication month",
        "cited_by_count": "Citation count reported by OpenAlex",
        "authorships": "Author and affiliation metadata reported by OpenAlex",
        "primary_topic_name": "OpenAlex primary topic",
        "primary_subfield": "OpenAlex primary topic subfield",
        "topic_names": "OpenAlex topic labels",
        "keyword_names": "OpenAlex keyword labels",
        "venue_name": "Source venue from the primary OpenAlex location",
        "concept_group": "Derived broad AI research category",
        "abstract_length": "Token count reconstructed from the OpenAlex abstract index",
    }
    rows = []
    for column in df.columns:
        series = df[column]
        if pd.api.types.is_bool_dtype(series):
            data_type = "bool"
        elif pd.api.types.is_integer_dtype(series):
            data_type = "int"
        elif pd.api.types.is_numeric_dtype(series):
            data_type = "float"
        elif pd.api.types.is_datetime64_any_dtype(series):
            data_type = "datetime"
        else:
            data_type = "list/object" if series.map(
                lambda value: isinstance(value, (list, dict))
            ).any() else "string"
        rows.append({
            "column_name": column,
            "data_type": data_type,
            "description": descriptions.get(column, f"OpenAlex source or derived field: {column}"),
            "source": "derived" if column in engineered or column in {
                "primary_concept", "primary_topic_name", "primary_subfield",
                "topic_names", "keyword_names", "venue_name", "countries",
                "authors_count", "publication_quarter",
            } else "OpenAlex",
            "allowed_values": "",
            "missing_policy": "Preserve as missing; do not fabricate source metadata",
            "feature_type": "engineered" if column in engineered else "source/normalized",
        })
    return pd.DataFrame(rows)


def _write_quality_report(
    df: pd.DataFrame, metadata: Dict[str, Any], report_path: str
) -> None:
    missing = df.isna().sum().sort_values(ascending=False)
    missing_rows = [
        f"<tr><td>{html.escape(str(column))}</td><td>{int(count)}</td>"
        f"<td>{count / max(len(df), 1):.1%}</td></tr>"
        for column, count in missing.items() if count
    ]
    invalid_urls = 0
    if "doi" in df:
        doi_values = df["doi"].dropna().astype(str)
        invalid_urls = int((~doi_values.str.match(r"^https?://doi\.org/", case=False)).sum())
    duplicate_ids = int(df["id"].duplicated().sum()) if "id" in df else 0
    institution_id = metadata["institution_id"]
    ai_subfield_id = metadata["ai_subfield_id"]
    venue_missing = int(df["venue_name"].eq("Unknown").sum())
    abstract_missing = int(df["abstract_length"].eq(0).sum())
    citations = df["cited_by_count"]
    lower_quartile, upper_quartile = citations.quantile([0.25, 0.75])
    interquartile_range = upper_quartile - lower_quartile
    citation_outliers = int(
        (
            (citations < lower_quartile - 1.5 * interquartile_range)
            | (citations > upper_quartile + 1.5 * interquartile_range)
        ).sum()
    )
    institution_visible = sum(
        any(
            institution.get("id", "").rsplit("/", 1)[-1] == institution_id
            for authorship in _records(authorships)
            for institution in _records(authorship.get("institutions"))
        )
        for authorships in df["authorships"]
    )
    ai_topic_visible = sum(
        any(
            (topic.get("subfield") or {}).get("id", "").rsplit("/", 1)[-1] == ai_subfield_id
            for topic in _records(topics)
        )
        for topics in df["topics"]
    )
    yearly = metadata.get("yearly_counts", {})
    yearly_rows = "".join(
        f"<tr><td>{html.escape(year)}</td><td>{values['available']}</td>"
        f"<td>{values['sampled']}</td></tr>"
        for year, values in sorted(yearly.items())
    )
    missing_table = "".join(missing_rows) or "<tr><td colspan='3'>Không có giá trị thiếu</td></tr>"
    content = f"""<!doctype html>
<html lang="vi"><meta charset="utf-8"><title>Báo cáo chất lượng dữ liệu</title>
<style>body{{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 20px;color:#243044}}
table{{border-collapse:collapse;width:100%;margin:18px 0}}th,td{{border:1px solid #d8dee8;padding:8px;text-align:left}}
th{{background:#edf2f8}}.cards{{display:flex;gap:14px;flex-wrap:wrap}}.card{{padding:14px 20px;background:#f1f5f9;border-radius:8px}}</style>
<h1>Báo cáo chất lượng dữ liệu</h1>
<p>Nguồn: OpenAlex Works API; truy vấn affiliation Tsinghua và topic subfield AI.
Thời gian: {html.escape(metadata['from_date'])} đến {html.escape(metadata['to_date'])}.</p>
<div class="cards"><div class="card">Bản ghi: <b>{len(df):,}</b></div>
<div class="card">Số cột: <b>{len(df.columns)}</b></div>
<div class="card">Trùng ID: <b>{duplicate_ids}</b></div>
<div class="card">DOI không đúng URL: <b>{invalid_urls}</b></div>
<div class="card">Venue thiếu: <b>{venue_missing}</b></div>
<div class="card">Abstract thiếu: <b>{abstract_missing}</b></div>
<div class="card">Ngoại lệ trích dẫn theo IQR: <b>{citation_outliers}</b></div>
<div class="card">OpenAlex trong phạm vi: <b>{metadata['available_records']:,}</b></div></div>
<p>Trong raw, {institution_visible}/{len(df)} bản ghi có affiliation hiển thị mã tổ chức đã lọc;
{ai_topic_visible}/{len(df)} có topic hiển thị đúng subfield AI. Bộ lọc truy vấn API dùng chính xác
mã tổ chức và subfield ghi trong metadata; bản ghi thiếu ID affiliation hiển thị được giữ và đánh dấu
để kiểm tra nguồn.</p>
<h2>Mẫu theo năm</h2><table><thead><tr><th>Năm</th><th>Số bản ghi phù hợp theo OpenAlex</th>
<th>Số bản ghi đã lấy</th></tr></thead><tbody>{yearly_rows}</tbody></table>
<h2>Trường có giá trị thiếu</h2><table><thead><tr><th>Cột</th><th>Số thiếu</th><th>Tỷ lệ</th>
</tr></thead><tbody>{missing_table}</tbody></table>
<h2>Kiểm tra</h2><ul><li>Loại dữ liệu và kiểu lồng nhau được giữ theo metadata OpenAlex.</li>
<li>Trùng lặp được loại theo OpenAlex work ID.</li><li>Không tự điền venue, abstract hoặc URL code/dataset bị thiếu.</li>
<li>Quota lấy mẫu được phân bổ tỷ lệ theo số bản ghi OpenAlex từng năm; mỗi năm tối đa 200 bài.
Đây là mẫu theo thứ tự API, không phải mẫu ngẫu nhiên.</li>
<li>Các bảng research group, LLM/model, dataset, dự án mã nguồn mở và ranking chỉ có header
cho đến khi có nguồn xác minh riêng; không tạo dữ liệu suy đoán.</li></ul></html>"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(content, encoding="utf-8")


def _write_storytelling_report(
    df: pd.DataFrame,
    yearly: pd.DataFrame,
    metadata: Dict[str, Any],
    report_path: str,
) -> None:
    total = len(df)
    citations = df["cited_by_count"]
    median_citations = float(citations.median()) if total else 0
    max_index = citations.idxmax() if total else None
    max_title = str(df.loc[max_index, "title"]) if max_index is not None else "—"
    max_citations = int(citations.loc[max_index]) if max_index is not None else 0
    group_counts = df["concept_group"].value_counts()
    top_groups = ", ".join(
        f"{html.escape(str(group))}: {count:,}"
        for group, count in group_counts.head(4).items()
    )
    primary_topics = df["primary_topic_name"].value_counts().head(5)
    topic_summary = ", ".join(
        f"{html.escape(str(topic))} ({count})" for topic, count in primary_topics.items()
    )
    venue_missing = int(df["venue_name"].eq("Unknown").sum())
    abstract_missing = int(df["abstract_length"].eq(0).sum())
    international_count = int(df["is_international"].sum())
    r_squared = float(df[["publication_year", "cited_by_count"]].corr().iloc[0, 1] ** 2)
    year_counts = metadata.get("yearly_counts", {})
    sample_years = sorted(int(year) for year in year_counts)
    year_span = f"{sample_years[0]}–{sample_years[-1]}" if sample_years else "không xác định"
    charts = "".join(
        f'<figure class="chart-card"><button class="chart-zoom" type="button" '
        f'data-full-image="../figures/{filename}" data-caption="{html.escape(label, quote=True)}" '
        f'aria-label="Phóng to biểu đồ: {html.escape(label, quote=True)}">'
        f'<img loading="lazy" src="../figures/{filename}" alt="{html.escape(label, quote=True)}">'
        f'<span class="zoom-hint" aria-hidden="true">⌕ Xem chi tiết</span></button>'
        f"<figcaption>{html.escape(label)}</figcaption></figure>"
        for filename, label in STATIC_CHARTS
    )
    annual_rows = "".join(
        f"<tr><td>{int(row.year)}</td><td>{int(row.sampled_papers):,}</td>"
        f"<td>{int(row.citation_count_in_sample):,}</td></tr>"
        for row in yearly.itertuples()
    )
    content = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tsinghua AI — Câu chuyện dữ liệu</title>
<style>
*{{box-sizing:border-box}}
:root{{--navy:#102238;--blue:#235d83;--teal:#2a938f;--gold:#e2b866;--ink:#182b3d;--muted:#627487;--paper:#f4f7fa;--line:#e1e8ee}}
html{{scroll-behavior:smooth;scroll-padding-top:76px}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.72 "Segoe UI",system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:#176b91;text-decoration:none}}a:hover{{color:#0f4769;text-decoration:underline}}
.topbar{{position:sticky;top:0;z-index:20;background:rgba(16,34,56,.96);backdrop-filter:blur(12px);border-bottom:1px solid #ffffff1c}}
.topbar-inner{{max-width:1180px;margin:auto;padding:0 24px;min-height:58px;display:flex;align-items:center;justify-content:space-between;gap:18px}}
.brand{{color:#fff;font-weight:700;letter-spacing:.03em;white-space:nowrap}}.brand span{{color:var(--gold)}}
.nav-links{{display:flex;gap:22px;align-items:center;font-size:.88rem}}.nav-links a{{color:#d7e4ee}}
.hero{{position:relative;overflow:hidden;padding:clamp(58px,9vw,112px) 24px 78px;color:white;background:radial-gradient(ellipse at 80% 10%,#2a938f55,transparent 36%),linear-gradient(125deg,#102238 0%,#193d5d 58%,#286c7d 100%)}}
.hero::after{{content:"";position:absolute;width:430px;height:430px;border:1px solid #ffffff1a;border-radius:50%;right:-130px;bottom:-275px;box-shadow:0 0 0 48px #ffffff08,0 0 0 96px #ffffff06}}
.hero-inner{{position:relative;z-index:1;max-width:1120px;margin:auto}}
.eyebrow{{display:inline-flex;align-items:center;gap:9px;color:#f2d69f;font-size:.76rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}
.eyebrow::before{{content:"";width:25px;height:2px;background:var(--gold)}}
h1{{max-width:850px;margin:18px 0;font-size:clamp(2.35rem,6vw,4.7rem);line-height:1.04;letter-spacing:-.045em}}
.hero-copy{{max-width:760px;color:#d6e4ed;font-size:1.08rem}}
.hero-meta{{display:flex;flex-wrap:wrap;gap:9px;margin-top:27px}}
.pill{{padding:7px 12px;border:1px solid #ffffff2b;border-radius:99px;color:#e5eef4;font-size:.82rem;background:#ffffff0b}}
.page-wrap{{max-width:1120px;margin:-27px auto 0;padding:0 22px 60px;position:relative;z-index:2}}
.section{{margin:20px 0;padding:clamp(22px,4vw,38px);background:#fff;border:1px solid #e9eef2;border-radius:18px;box-shadow:0 12px 34px #16324a0c}}
.section-heading{{display:flex;align-items:flex-start;gap:15px;margin-bottom:18px}}
.section-number{{flex:0 0 auto;color:var(--teal);font-size:.78rem;font-weight:800;letter-spacing:.12em;padding-top:7px}}
h2{{margin:0;color:var(--navy);font-size:clamp(1.35rem,3vw,1.85rem);line-height:1.25;letter-spacing:-.02em}}
.section p{{color:#405366}}.section-intro{{max-width:860px}}
.note{{margin:20px 0;padding:16px 18px;background:#fff8e9;border:1px solid #f1e3c4;border-left:4px solid var(--gold);border-radius:0 12px 12px 0;color:#5c4d35}}
.stats{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:24px}}
.stat{{padding:18px 20px;border:1px solid var(--line);border-radius:13px;background:linear-gradient(145deg,#fff,#f5f9fb)}}
.stat strong{{display:block;color:var(--blue);font-size:clamp(1.35rem,3vw,1.8rem);line-height:1.25;overflow-wrap:anywhere}}
.stat span{{display:block;margin-top:5px;color:var(--muted);font-size:.85rem}}
.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin-top:18px}}
table{{width:100%;border-collapse:collapse;min-width:440px;font-variant-numeric:tabular-nums}}
th,td{{padding:10px 14px;border-bottom:1px solid var(--line);text-align:left}}
th{{background:#f2f7f9;color:#254b67;font-size:.84rem}}tbody tr:last-child td{{border-bottom:0}}tbody tr:hover{{background:#f7fafb}}
.gallery{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:22px}}
.chart-card{{min-width:0;overflow:hidden;margin:0;padding:10px;border:1px solid var(--line);border-radius:14px;background:#fbfcfd;transition:transform .2s,box-shadow .2s,border-color .2s}}
.chart-card:hover{{transform:translateY(-3px);border-color:#b6d1dc;box-shadow:0 12px 24px #1a425315}}
.chart-zoom{{position:relative;display:block;width:100%;padding:0;border:0;border-radius:9px;background:#fff;cursor:zoom-in;overflow:hidden;text-align:left}}
.chart-zoom:focus-visible,.nav-links a:focus-visible,.resource-link:focus-visible{{outline:3px solid var(--gold);outline-offset:3px}}
.chart-zoom img{{display:block;width:100%;height:auto;transition:transform .25s}}
.chart-card:hover .chart-zoom img{{transform:scale(1.015)}}
.zoom-hint{{position:absolute;right:10px;bottom:10px;padding:5px 9px;border-radius:99px;background:#102238dc;color:#fff;font-size:.75rem;opacity:0;transform:translateY(4px);transition:opacity .2s,transform .2s}}
.chart-card:hover .zoom-hint,.chart-zoom:focus-visible .zoom-hint{{opacity:1;transform:none}}
.chart-card figcaption{{padding:11px 5px 3px;color:#334b5f;font-size:.9rem;font-weight:600}}
.resource-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:18px}}
.resource-link{{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:#f8fafb;color:#244d6a;font-weight:600}}
.resource-link:hover{{background:#eef6f7;text-decoration:none;border-color:#b6d1dc}}
.resource-link span:last-child{{color:var(--teal);font-size:1.15rem}}
.dialog{{width:min(96vw,1500px);max-width:none;max-height:96vh;padding:0;border:1px solid #ffffff28;border-radius:16px;background:#101923;color:#fff;box-shadow:0 28px 100px #0009}}
.dialog::backdrop{{background:#07111de8;backdrop-filter:blur(5px)}}
.dialog-header{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 16px;color:#edf3f6}}
.dialog-title{{font-size:.92rem;font-weight:600}}
.dialog-close{{width:38px;height:38px;display:grid;place-items:center;border:1px solid #ffffff30;border-radius:50%;background:#ffffff12;color:#fff;font-size:1.4rem;cursor:pointer}}
.dialog-close:hover{{background:#ffffff28}}.dialog-image-wrap{{display:grid;place-items:center;padding:0 14px 14px}}
.dialog-image{{display:block;max-width:100%;max-height:calc(96vh - 78px);width:auto;height:auto;object-fit:contain;border-radius:8px}}
footer{{padding:34px 24px;background:var(--navy);color:#c8d7e1;text-align:center;font-size:.88rem}}
footer a{{color:#f0cd87}}footer p{{margin:4px}}
@media(max-width:720px){{.nav-links{{gap:13px;font-size:.8rem}}.topbar-inner{{padding:0 16px}}.brand{{font-size:.9rem}}.stats{{grid-template-columns:repeat(2,minmax(0,1fr))}}.gallery{{grid-template-columns:1fr}}.page-wrap{{padding:0 14px 40px}}}}
@media(max-width:430px){{.nav-links a:nth-child(2){{display:none}}.hero{{padding-left:19px;padding-right:19px}}.stats{{gap:8px}}.stat{{padding:13px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*,*::before,*::after{{transition:none!important}}}}
</style></head><body>
<nav class="topbar" aria-label="Điều hướng báo cáo"><div class="topbar-inner">
<a class="brand" href="#top">TSINGHUA <span>AI</span></a>
<div class="nav-links"><a href="#overview">Tổng quan</a><a href="#charts">Biểu đồ</a><a href="#resources">Tài nguyên</a></div>
</div></nav>
<header class="hero" id="top"><div class="hero-inner">
<div class="eyebrow">Dữ liệu nghiên cứu · OpenAlex</div>
<h1>Bức tranh nghiên cứu<br>AI tại Tsinghua</h1>
<p class="hero-copy">Khám phá công bố, xu hướng và hợp tác nghiên cứu qua dữ liệu OpenAlex
được lọc theo tổ chức và chủ đề trí tuệ nhân tạo.</p>
<div class="hero-meta"><span class="pill">清华大学 · Đại học Thanh Hoa</span>
<span class="pill">Artificial Intelligence subfield</span>
<span class="pill">{html.escape(metadata['from_date'])} — {html.escape(metadata['to_date'])}</span></div>
</div></header><main class="page-wrap">
<section class="section" id="overview"><div class="section-heading"><span class="section-number">01</span><h2>Câu chuyện chính</h2></div>
<p>Thay vì lấy mọi công bố có affiliation Tsinghua, bộ dữ liệu lần này chỉ nhận các công trình
được OpenAlex gắn ít nhất một topic thuộc subfield AI. Trong phạm vi truy vấn có
<strong>{metadata['available_records']:,} công trình</strong>; bộ dữ liệu phân tích là mẫu tối đa
{metadata['sample_target']:,} bài, lấy theo quota tỷ lệ với số công trình từng năm để bao phủ
{html.escape(year_span)}.</p>
<p>Raw có {sum(any(i.get('id', '').rsplit('/', 1)[-1] == metadata['institution_id'] for a in _records(authorships) for i in _records(a.get('institutions'))) for authorships in df['authorships']):,}/{total:,}
bản ghi hiển thị mã Tsinghua trong authorships và {sum(any((topic.get('subfield') or {}).get('id', '').rsplit('/', 1)[-1] == metadata['ai_subfield_id'] for topic in _records(topics)) for topics in df['topics']):,}/{total:,}
có topic hiển thị đúng subfield AI. Sai khác affiliation hiển thị được nêu rõ trong báo cáo chất lượng.</p>
<p class="note"><strong>Đọc đúng phạm vi:</strong> đây là mẫu từ OpenAlex, không phải danh mục đầy đủ
các công trình AI của trường. Topic và affiliation do OpenAlex gán; kết quả phụ thuộc chất lượng
metadata của nguồn. Quota mẫu không ngẫu nhiên nên các thống kê mô tả mẫu, không đại diện chắc chắn
cho toàn bộ sản lượng hay chất lượng nghiên cứu của Tsinghua.</p>
<div class="stats"><div class="stat"><strong>{total:,}</strong><span>Bài trong mẫu</span></div>
<div class="stat"><strong>{metadata['available_records']:,}</strong><span>Bài phù hợp theo truy vấn</span></div>
<div class="stat"><strong>{year_span}</strong><span>Khoảng năm</span></div>
<div class="stat"><strong>{int(citations.sum()):,}</strong><span>Lượt trích dẫn trong mẫu</span></div>
<div class="stat"><strong>{median_citations:.0f}</strong><span>Trung vị trích dẫn/bài</span></div>
<div class="stat"><strong>{international_count:,}</strong><span>Bài có nhiều quốc gia</span></div></div></section>
<section class="section"><div class="section-heading"><span class="section-number">02</span><h2>Mẫu trải dài theo thời gian</h2></div>
<p>Mỗi năm được lấy theo tỷ lệ quy mô kết quả OpenAlex, tối đa 200 bài/năm. Đường thời gian bên dưới
cho thấy số bản ghi đã lấy và có thể dùng để khám phá mẫu, nhưng không nên coi là số công bố thực tế
của từng năm khi còn giới hạn lấy mẫu. Năm 2026 chỉ tính đến ngày truy vấn nên là năm chưa trọn vẹn.</p>
<div class="table-wrap"><table><thead><tr><th>Năm</th><th>Mẫu đã thu thập</th><th>Trích dẫn trong mẫu</th></tr></thead>
<tbody>{annual_rows}</tbody></table></div></section>
<section class="section"><div class="section-heading"><span class="section-number">03</span><h2>Trích dẫn và metadata</h2></div>
<p>Trong mẫu, số trích dẫn cao nhất là <strong>{max_citations:,}</strong> cho bài
“{html.escape(max_title)}”; R² mô tả giữa năm xuất bản và lượt trích dẫn là
<strong>{r_squared:.3f}</strong>. Đây không phải quan hệ nhân quả; bài mới có ít thời gian tích lũy
trích dẫn hơn. Có {venue_missing:,}/{total:,} venue chưa được OpenAlex cung cấp và
{abstract_missing:,}/{total:,} abstract không có chỉ mục từ để tính độ dài. Không suy diễn venue
hay nội dung abstract bị thiếu.</p>
<p>Nhóm khái niệm heuristic trong mẫu: {top_groups}. Các primary topic gặp nhiều nhất:
{topic_summary}. Việc nhóm chủ đề là hỗ trợ trực quan, không thay thế taxonomy gốc OpenAlex.</p>
</section>
<section class="section" id="charts"><div class="section-heading"><span class="section-number">04</span><h2>Bộ biểu đồ khám phá</h2></div>
<p class="section-intro">Chọn bất kỳ biểu đồ nào để mở ảnh lớn, xem rõ nhãn và chi tiết. Nhấn nền tối hoặc phím Escape để đóng.</p>
<div class="gallery">{charts}</div></section>
<section class="section" id="resources"><div class="section-heading"><span class="section-number">05</span><h2>Biểu đồ tương tác & tài nguyên</h2></div>
<p>Ba biểu đồ Plotly hỗ trợ hover, zoom và khám phá dữ liệu; mở từng biểu đồ để dùng thanh công cụ tương tác.</p>
<div class="resource-grid">
<a class="resource-link" href="../figures/interactive_chart_1.html" target="_blank" rel="noopener"><span>Dòng thời gian tương tác</span><span>↗</span></a>
<a class="resource-link" href="../figures/interactive_chart_2.html" target="_blank" rel="noopener"><span>Scatter tương tác</span><span>↗</span></a>
<a class="resource-link" href="../figures/interactive_chart_3.html" target="_blank" rel="noopener"><span>Treemap tương tác</span><span>↗</span></a>
<a class="resource-link" href="dashboard.html" target="_blank" rel="noopener"><span>Dashboard tổng hợp</span><span>↗</span></a>
<a class="resource-link" href="data_quality_report.html"><span>Báo cáo chất lượng dữ liệu</span><span>↗</span></a></div>
<p>Dữ liệu thô JSON ở <code>data/raw/openalex_raw.json</code>; dữ liệu sạch và đặc trưng ở
<code>data/processed/</code> và <code>data/final/</code>; bảng bài báo và nhà nghiên cứu xuất CSV.</p>
</section></main>
<dialog class="dialog" aria-label="Xem biểu đồ kích thước lớn"><div class="dialog-header">
<div class="dialog-title" id="dialog-title"></div><button class="dialog-close" type="button" aria-label="Đóng biểu đồ">×</button>
</div><div class="dialog-image-wrap"><img class="dialog-image" alt=""></div></dialog>
<footer>
Nguồn: <a href="https://api.openalex.org/works">OpenAlex Works API</a> · Tổ chức:
{html.escape(metadata['institution_id'])} · AI subfield:
{html.escape(metadata['ai_subfield_id'])} · Truy vấn đếm trả về {metadata['available_records']:,} công trình.
</footer>
<script>
(() => {{
  const dialog = document.querySelector(".dialog");
  const dialogImage = dialog.querySelector(".dialog-image");
  const dialogTitle = document.querySelector("#dialog-title");
  const closeButton = dialog.querySelector(".dialog-close");

  document.querySelectorAll(".chart-zoom").forEach((button) => {{
    button.addEventListener("click", () => {{
      dialogImage.src = button.dataset.fullImage;
      dialogImage.alt = button.dataset.caption;
      dialogTitle.textContent = button.dataset.caption;
      dialog.showModal();
    }});
  }});

  closeButton.addEventListener("click", () => dialog.close());
  document.addEventListener("keydown", (event) => {{
    if (event.key === "Escape" && dialog.open) dialog.close();
  }});
  dialog.addEventListener("click", (event) => {{
    if (event.target === dialog) dialog.close();
  }});
  dialog.addEventListener("close", () => dialogImage.removeAttribute("src"));
}})();
</script></body></html>"""
    output = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
