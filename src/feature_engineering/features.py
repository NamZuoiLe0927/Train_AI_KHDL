"""Feature engineering module for creating derived features."""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, List


def create_features(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Create derived features for analysis and visualization.

    Args:
        df: Cleaned DataFrame.
        config: Configuration dictionary containing the final output path.

    Returns:
        DataFrame with additional features.
    """
    df = df.copy()

    # Time-based features
    current_year = pd.Timestamp.now().year
    df["paper_age"] = current_year - df["publication_year"]
    df["paper_age"] = df["paper_age"].clip(lower=0)

    # Citation features
    df["citations_per_year"] = df.apply(
        lambda row: row["cited_by_count"] / max(row["paper_age"], 1), axis=1
    )

    # Categorize citation level
    def citation_level(cited):
        if cited == 0:
            return "uncited"
        elif cited <= 10:
            return "low"
        elif cited <= 50:
            return "medium"
        elif cited <= 200:
            return "high"
        else:
            return "very_high"

    df["citation_level"] = df["cited_by_count"].apply(citation_level)

    # Author collaboration features
    df["single_author"] = df["authors_count"] == 1
    df["large_team"] = df["authors_count"] >= 10

    # Concept features
    df["concept_group"] = df.apply(
        lambda row: group_concept(
            row["primary_topic_name"], row["primary_concept"], row["topic_names"]
        ),
        axis=1,
    )

    # Venue tier (simplified)
    top_venues = {
        "NeurIPS", "ICML", "ICLR", "ACL", "EMNLP", "NAACL",
        "AAAI", "IJCAI", "CVPR", "ICCV", "ECCV", "KDD",
        "WWW", "SIGIR", "Nature", "Science", "Cell"
    }
    df["is_top_venue"] = df["venue_name"].apply(lambda x: x in top_venues)

    # Text length features (if abstract available)
    if "abstract_inverted_index" in df.columns:
        def abstract_length(abstract_idx):
            if isinstance(abstract_idx, dict):
                return sum(len(v) for v in abstract_idx.values())
            return 0
        df["abstract_length"] = df["abstract_inverted_index"].apply(abstract_length)
    else:
        df["abstract_length"] = 0

    # Year-month for time series
    df["year_month"] = df["publication_year"].astype(str) + "-" + df["publication_month"].astype(str).str.zfill(2)

    # Save final data
    final_path = Path(config["storage"]["final_path"])
    final_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(final_path, index=False)
    print(f"    Feature-engineered data saved to {final_path}")

    return df


def group_concept(topic: str, concept: str, topic_names: List[str]) -> str:
    """Group OpenAlex AI topics using topic and concept metadata."""
    labels = [topic, concept]
    if isinstance(topic_names, list):
        labels.extend(topic_names)
    concept_lower = " ".join(str(label) for label in labels).lower()

    nlp_keywords = ["language", "nlp", "linguistic", "translation", "text", "speech", "bert", "gpt", "llm", "transformer"]
    cv_keywords = ["vision", "image", "video", "object detection", "segmentation", "face", "visual"]
    robotics_keywords = ["robot", "control", "autonomous", "navigation", "manipulation"]
    ai_systems_keywords = ["system", "distributed", "parallel", "cloud", "edge", "hardware", "accelerator"]
    ml_keywords = ["machine learning", "deep learning", "neural network", "reinforcement learning", "optimization"]

    if any(kw in concept_lower for kw in cv_keywords):
        return "Computer Vision"
    if any(kw in concept_lower for kw in robotics_keywords):
        return "Robotics"
    if any(kw in concept_lower for kw in ai_systems_keywords):
        return "AI Systems"
    if any(kw in concept_lower for kw in nlp_keywords):
        return "NLP"
    if any(kw in concept_lower for kw in ml_keywords):
        return "Machine Learning"
    return "Other"