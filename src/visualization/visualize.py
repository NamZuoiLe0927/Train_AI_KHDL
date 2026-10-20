"""Visualization module for creating static and interactive charts."""

import json
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
from wordcloud import WordCloud


CONCEPT_GROUP_LABELS = {
    "NLP": "Xử lý ngôn ngữ tự nhiên",
    "Computer Vision": "Thị giác máy tính",
    "Machine Learning": "Học máy",
    "Robotics": "Robot học",
    "AI Systems": "Hệ thống trí tuệ nhân tạo",
    "Other": "Khác",
}

PRIMARY_CONCEPT_LABELS = {
    "Medicine": "Y học",
    "Computer vision": "Thị giác máy tính",
    "Artificial intelligence": "Trí tuệ nhân tạo",
    "Osimertinib": "Thuốc osimertinib",
    "Nivolumab": "Thuốc nivolumab",
    "Afatinib": "Thuốc afatinib",
    "Teriparatide": "Thuốc teriparatide",
    "Chromatography": "Sắc ký",
    "Radioimmunotherapy": "Xạ trị miễn dịch",
    "Durvalumab": "Thuốc durvalumab",
    "Nonsynonymous substitution": "Đột biến thay thế không đồng nghĩa",
    "Stroma": "Mô đệm",
    "Lymphoepithelioma-like carcinoma": "Ung thư dạng lympho biểu mô",
    "Segmentation": "Phân đoạn ảnh",
    "Asthma": "Hen suyễn",
    "Alectinib": "Thuốc alectinib",
    "CDX2": "Yếu tố CDX2",
    "Downregulation and upregulation": "Điều hòa giảm và điều hòa tăng",
    "Albendazole": "Thuốc albendazole",
    "Resolution (logic)": "Độ phân giải",
    "Fever of unknown origin": "Sốt không rõ nguyên nhân",
    "Emperipolesis": "Hiện tượng emperipolesis",
    "Hyperphosphatemia": "Tăng phosphat máu",
    "Cascade": "Chuỗi xử lý",
    "Antibody": "Kháng thể",
    "Computer science": "Khoa học máy tính",
    "Kampo": "Y học Kampo",
    "Stromal cell": "Tế bào mô đệm",
}

FEATURE_LABELS = {
    "cited_by_count": "Số lượt trích dẫn",
    "authors_count": "Số tác giả",
    "paper_age": "Tuổi bài báo",
    "citations_per_year": "Số trích dẫn mỗi năm",
    "countries_count": "Số quốc gia",
    "abstract_length": "Độ dài tóm tắt",
}

def translate_concept_group(value: str) -> str:
    """Translate a research-area category for chart display."""
    return CONCEPT_GROUP_LABELS.get(value, "Lĩnh vực nghiên cứu khác")


def translate_primary_concept(value: str) -> str:
    """Translate a source concept for chart display without changing source data."""
    if value.startswith("Modality (human"):
        return "Phương thức tương tác người – máy"
    return PRIMARY_CONCEPT_LABELS.get(value, "Khái niệm khoa học khác")


def create_visualizations(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Create all required static and interactive visualizations.

    Args:
        df: Feature-engineered DataFrame.
        config: Configuration dictionary.
    """
    figure_dir = Path(config["storage"]["figure_dir"])
    figure_dir.mkdir(parents=True, exist_ok=True)

    # Set style
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette("husl")

    print("    Creating static charts...")

    # 1. Histogram - Citation distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df["cited_by_count"].clip(upper=200), bins=50, edgecolor="black", alpha=0.7)
    ax.set_xlabel("Số lượt trích dẫn (giới hạn ở 200)")
    ax.set_ylabel("Số bài báo")
    ax.set_title("Phân bố số lượt trích dẫn")
    plt.tight_layout()
    plt.savefig(figure_dir / "histogram_citations.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2. Boxplot - Citations by concept group
    fig, ax = plt.subplots(figsize=(12, 6))
    df_plot = df[df["cited_by_count"] <= 200]
    df_plot = df_plot.assign(
        concept_group_vi=df_plot["concept_group"].map(translate_concept_group)
    )
    sns.boxplot(data=df_plot, x="concept_group_vi", y="cited_by_count", ax=ax)
    ax.set_xlabel("Lĩnh vực nghiên cứu")
    ax.set_ylabel("Số lượt trích dẫn")
    ax.set_title("Phân bố trích dẫn theo lĩnh vực nghiên cứu")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(figure_dir / "boxplot_citations_by_area.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3. Violin Plot - Citations by venue tier
    fig, ax = plt.subplots(figsize=(10, 6))
    df_plot = df[df["cited_by_count"] <= 200]
    df_plot = df_plot.assign(
        venue_tier_vi=df_plot["is_top_venue"].map({True: "Có", False: "Không"})
    )
    sns.violinplot(data=df_plot, x="venue_tier_vi", y="cited_by_count", ax=ax)
    ax.set_xlabel("Hội nghị hoặc tạp chí hàng đầu")
    ax.set_ylabel("Số lượt trích dẫn")
    ax.set_title("Phân bố trích dẫn theo chất lượng tạp chí, hội nghị")
    plt.tight_layout()
    plt.savefig(figure_dir / "violin_citations_venue.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. Line Chart - Papers per year
    yearly = df.groupby("publication_year").size().reset_index(name="count")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(yearly["publication_year"], yearly["count"], marker="o", linewidth=2, markersize=8)
    ax.set_xlabel("Năm xuất bản")
    ax.set_ylabel("Số bài báo")
    ax.set_title("Số bài báo theo năm")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_dir / "line_papers_per_year.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 5. Area Chart - Papers by concept group over time
    area_data = df.groupby(["publication_year", "concept_group"]).size().reset_index(name="count")
    area_pivot = area_data.pivot(index="publication_year", columns="concept_group", values="count").fillna(0)
    area_pivot.columns = [translate_concept_group(group) for group in area_pivot.columns]
    fig, ax = plt.subplots(figsize=(12, 6))
    area_pivot.plot.area(ax=ax, alpha=0.6)
    ax.set_xlabel("Năm xuất bản")
    ax.set_ylabel("Số bài báo")
    ax.set_title("Số bài báo theo lĩnh vực nghiên cứu qua các năm")
    ax.legend(title="Lĩnh vực nghiên cứu", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(figure_dir / "area_papers_by_area.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 6. Scatter + Regression - Year vs Citations
    fig, ax = plt.subplots(figsize=(10, 6))
    df_plot = df[df["cited_by_count"] <= 500]
    ax.scatter(df_plot["publication_year"], df_plot["cited_by_count"], alpha=0.5, s=20)

    # Add regression line
    slope, intercept = np.polyfit(
        df_plot["publication_year"], df_plot["cited_by_count"], 1
    )
    r_value = np.corrcoef(
        df_plot["publication_year"], df_plot["cited_by_count"]
    )[0, 1]
    x_line = np.array([df_plot["publication_year"].min(), df_plot["publication_year"].max()])
    y_line = slope * x_line + intercept
    ax.plot(
        x_line, y_line, color="red", linewidth=2,
        label=f"Hồi quy tuyến tính (R² = {r_value**2:.3f})"
    )
    ax.set_xlabel("Năm xuất bản")
    ax.set_ylabel("Số lượt trích dẫn")
    ax.set_title("Năm xuất bản và số lượt trích dẫn")
    ax.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "scatter_year_vs_citations.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 7. Correlation Heatmap
    numeric_cols = [
        "cited_by_count", "authors_count", "paper_age",
        "citations_per_year", "countries_count", "abstract_length"
    ]
    corr_matrix = df[numeric_cols].rename(columns=FEATURE_LABELS).corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title("Ma trận tương quan giữa các đặc trưng số")
    plt.tight_layout()
    plt.savefig(figure_dir / "heatmap_correlation.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 8. Treemap - Papers by concept group (static)
    treemap_data = df["concept_group"].value_counts().reset_index()
    treemap_data.columns = ["concept_group", "count"]
    treemap_data["concept_group"] = treemap_data["concept_group"].map(translate_concept_group)
    fig, ax = plt.subplots(figsize=(12, 8))
    # Simple bar chart as static treemap alternative
    bars = ax.barh(treemap_data["concept_group"], treemap_data["count"])
    ax.set_xlabel("Số bài báo")
    ax.set_title("Số bài báo theo lĩnh vực nghiên cứu")
    for bar, count in zip(bars, treemap_data["count"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                str(count), va="center")
    plt.tight_layout()
    plt.savefig(figure_dir / "treemap_concept_groups.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 9. WordCloud from titles
    all_titles = " ".join(df["title"].dropna().astype(str))
    if all_titles.strip():
        fig, ax = plt.subplots(figsize=(15, 7))
        wordcloud = WordCloud(
            width=1200, height=600,
            background_color="white",
            max_words=100,
            colormap="viridis"
        ).generate(all_titles)
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Đám mây từ khóa từ tiêu đề bài báo (nguyên văn)", fontsize=16)
        plt.tight_layout()
        plt.savefig(figure_dir / "wordcloud_titles.png", dpi=300, bbox_inches="tight")
        plt.close()

    # 10. Co-author network using author IDs from OpenAlex.
    paper_authors = []
    author_paper_counts = {}
    for authorships in df["authorships"]:
        author_ids = []
        if isinstance(authorships, list):
            for authorship in authorships:
                author = authorship.get("author", {})
                author_id = author.get("id")
                if author_id:
                    author_ids.append(author_id)
                    author_paper_counts[author_id] = author_paper_counts.get(author_id, 0) + 1
        paper_authors.append(author_ids)

    top_authors = {
        author_id
        for author_id, _ in sorted(
            author_paper_counts.items(), key=lambda item: item[1], reverse=True
        )[:40]
    }
    coauthor_graph = nx.Graph()
    for author_id in top_authors:
        coauthor_graph.add_node(author_id, papers=author_paper_counts[author_id])
    for author_ids in paper_authors:
        selected = sorted(set(author_ids).intersection(top_authors))
        for index, source in enumerate(selected):
            for target in selected[index + 1:]:
                if coauthor_graph.has_edge(source, target):
                    coauthor_graph[source][target]["weight"] += 1
                else:
                    coauthor_graph.add_edge(source, target, weight=1)

    fig, ax = plt.subplots(figsize=(14, 10))
    if coauthor_graph.number_of_edges():
        positions = nx.spring_layout(coauthor_graph, seed=42, k=0.7)
        edge_widths = [
            0.5 + coauthor_graph[source][target]["weight"] * 0.35
            for source, target in coauthor_graph.edges()
        ]
        nx.draw_networkx_edges(
            coauthor_graph, positions, ax=ax, alpha=0.2, width=edge_widths,
            edge_color="#64748b",
        )
        node_sizes = [
            70 + coauthor_graph.nodes[node]["papers"] * 18
            for node in coauthor_graph.nodes()
        ]
        nx.draw_networkx_nodes(
            coauthor_graph, positions, ax=ax, node_size=node_sizes,
            node_color="#b8894d", alpha=0.85,
        )
        name_by_id = {}
        for authorships in df["authorships"]:
            if isinstance(authorships, list):
                for authorship in authorships:
                    author = authorship.get("author", {})
                    if author.get("id") in top_authors:
                        name_by_id[author["id"]] = author.get("display_name", author["id"])
        label_ids = sorted(
            top_authors,
            key=lambda author_id: author_paper_counts[author_id],
            reverse=True,
        )[:15]
        nx.draw_networkx_labels(
            coauthor_graph.subgraph(label_ids), positions, ax=ax,
            labels={author_id: name_by_id.get(author_id, author_id) for author_id in label_ids},
            font_size=7,
        )
        ax.set_title("Mạng lưới đồng tác giả (40 nhà nghiên cứu hoạt động nhiều nhất)")
    else:
        ax.text(0.5, 0.5, "Không đủ dữ liệu đồng tác giả để tạo mạng lưới",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Mạng lưới đồng tác giả")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(figure_dir / "network_coauthors.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"    Static charts saved to {figure_dir}")

    print("    Creating interactive charts...")

    # Interactive 1: Line Chart - Papers over time with filters
    fig1 = px.line(
        yearly, x="publication_year", y="count",
        title="Số bài báo theo thời gian",
        markers=True,
        labels={"publication_year": "Năm xuất bản", "count": "Số bài báo"}
    )
    fig1.update_layout(hovermode="x unified")

    # Interactive 2: Scatter - Year vs Citations with hover
    df_scatter = df[df["cited_by_count"] <= 500].copy()
    df_scatter["concept_group_vi"] = df_scatter["concept_group"].map(
        translate_concept_group
    )
    fig2 = px.scatter(
        df_scatter, x="publication_year", y="cited_by_count",
        color="concept_group_vi", size="authors_count",
        hover_data=["title", "venue_name", "countries"],
        title="Năm xuất bản và số lượt trích dẫn",
        labels={
            "publication_year": "Năm xuất bản",
            "cited_by_count": "Số lượt trích dẫn",
            "authors_count": "Số tác giả",
            "concept_group_vi": "Lĩnh vực nghiên cứu",
            "title": "Tiêu đề bài báo (nguyên văn)",
            "venue_name": "Tạp chí hoặc hội nghị",
            "countries": "Mã quốc gia",
        }
    )

    # Interactive 3: Treemap - Hierarchical: Concept Group -> Primary Concept
    treemap_df = df.groupby(["concept_group", "primary_concept"]).size().reset_index(name="count")
    treemap_df["concept_group_vi"] = treemap_df["concept_group"].map(
        translate_concept_group
    )
    treemap_df["primary_concept_vi"] = treemap_df["primary_concept"].map(
        translate_primary_concept
    )
    fig3 = px.treemap(
        treemap_df, path=["concept_group_vi", "primary_concept_vi"], values="count",
        title="Cấu trúc phân cấp các lĩnh vực nghiên cứu",
        labels={
            "concept_group_vi": "Lĩnh vực nghiên cứu",
            "primary_concept_vi": "Khái niệm chính",
            "count": "Số bài báo",
        }
    )

    # Save interactive charts as HTML
    for i, fig in enumerate([fig1, fig2, fig3], 1):
        html_path = figure_dir / f"interactive_chart_{i}.html"
        fig.write_html(html_path, include_plotlyjs="cdn")
        print(f"    Interactive chart {i} saved to {html_path}")


def create_dashboard(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Create a combined interactive dashboard HTML file.

    Args:
        df: Feature-engineered DataFrame.
        config: Configuration dictionary.
    """
    dashboard_path = Path(config["storage"]["dashboard_path"])
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)

    # Create subplots dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Số bài báo theo thời gian",
            "Trích dẫn theo lĩnh vực nghiên cứu",
            "Năm xuất bản và số lượt trích dẫn",
            "Tỷ lệ các lĩnh vực nghiên cứu"
        ),
        specs=[
            [{"type": "scatter"}, {"type": "box"}],
            [{"type": "scatter"}, {"type": "domain"}]
        ]
    )

    # 1. Line chart - Publications over time
    yearly = df.groupby("publication_year").size().reset_index(name="count")
    fig.add_trace(
        go.Scatter(x=yearly["publication_year"], y=yearly["count"],
                   mode="lines+markers", name="Bài báo/năm",
                   hovertemplate="Năm: %{x}<br>Số bài báo: %{y}<extra></extra>"),
        row=1, col=1
    )

    # 2. Box plot - Citations by concept group
    df_box = df[df["cited_by_count"] <= 200]
    for group in df_box["concept_group"].unique():
        group_data = df_box[df_box["concept_group"] == group]["cited_by_count"]
        fig.add_trace(
            go.Box(
                y=group_data, name=translate_concept_group(group), showlegend=False,
                hovertemplate="Số lượt trích dẫn: %{y}<extra>%{fullData.name}</extra>"
            ),
            row=1, col=2
        )

    # 3. Scatter - Year vs Citations
    df_scatter = df[df["cited_by_count"] <= 500]
    fig.add_trace(
        go.Scatter(
            x=df_scatter["publication_year"], y=df_scatter["cited_by_count"],
            mode="markers", marker=dict(size=4, opacity=0.5),
            name="Bài báo", showlegend=False,
            hovertemplate="Năm xuất bản: %{x}<br>Số lượt trích dẫn: %{y}<extra></extra>"
        ),
        row=2, col=1
    )

    # 4. Pie chart - Research area distribution
    area_counts = df["concept_group"].value_counts()
    fig.add_trace(
        go.Pie(
            labels=[translate_concept_group(area) for area in area_counts.index],
            values=area_counts.values,
            name="Lĩnh vực nghiên cứu",
            hovertemplate="%{label}<br>Số bài báo: %{value}<extra></extra>",
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=800,
        title_text="Nghiên cứu trí tuệ nhân tạo tại Đại học Thanh Hoa",
        showlegend=False
    )
    fig.update_xaxes(title_text="Năm xuất bản", row=1, col=1)
    fig.update_yaxes(title_text="Số bài báo", row=1, col=1)
    fig.update_xaxes(title_text="Lĩnh vực nghiên cứu", row=1, col=2)
    fig.update_yaxes(title_text="Số lượt trích dẫn", row=1, col=2)
    fig.update_xaxes(title_text="Năm xuất bản", row=2, col=1)
    fig.update_yaxes(title_text="Số lượt trích dẫn", row=2, col=1)

    fig.write_html(dashboard_path, include_plotlyjs="cdn")
    print(f"    Dashboard saved to {dashboard_path}")