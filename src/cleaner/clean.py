"""Data cleaning and normalization module."""

import pandas as pd
from pathlib import Path
from typing import Any, Dict


def clean_data(raw_data: list, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Clean and normalize raw data into a structured DataFrame.

    Args:
        raw_data: List of raw records from API.
        config: Configuration dictionary.

    Returns:
        Cleaned DataFrame.
    """
    # Keep nested OpenAlex metadata as nested columns instead of flattening every token.
    df = pd.DataFrame(raw_data)

    # Ensure required columns exist
    required_cols = ["id", "title", "publication_date", "cited_by_count", "authorships"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Convert date
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")
    df["publication_year"] = df["publication_date"].dt.year
    df["publication_month"] = df["publication_date"].dt.month
    df["publication_quarter"] = df["publication_date"].dt.quarter

    # Convert numeric fields
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0).astype(int)

    # Handle authorships - count authors
    def count_authors(authorships):
        if isinstance(authorships, list):
            return len(authorships)
        return 0

    df["authors_count"] = df["authorships"].apply(count_authors)

    # Extract primary concept
    def get_primary_concept(concepts):
        if isinstance(concepts, list) and len(concepts) > 0:
            return concepts[0].get("display_name", "Unknown")
        return "Unknown"

    if "concepts" in df.columns:
        df["primary_concept"] = df["concepts"].apply(get_primary_concept)
    else:
        df["primary_concept"] = "Unknown"

    def get_primary_topic_value(topic, key):
        if isinstance(topic, dict):
            value = topic.get(key)
            if isinstance(value, dict):
                return value.get("display_name", "Unknown")
            return value or "Unknown"
        return "Unknown"

    df["primary_topic_name"] = df.get("primary_topic", pd.Series(index=df.index)).apply(
        lambda topic: get_primary_topic_value(topic, "display_name")
    )
    df["primary_subfield"] = df.get("primary_topic", pd.Series(index=df.index)).apply(
        lambda topic: get_primary_topic_value(topic.get("subfield"), "display_name")
        if isinstance(topic, dict) else "Unknown"
    )
    df["topic_names"] = df.get("topics", pd.Series(index=df.index)).apply(
        lambda topics: [
            topic.get("display_name", "Unknown")
            for topic in topics
            if isinstance(topic, dict)
        ] if isinstance(topics, list) else []
    )
    df["keyword_names"] = df.get("keywords", pd.Series(index=df.index)).apply(
        lambda keywords: [
            keyword.get("display_name", "Unknown")
            for keyword in keywords
            if isinstance(keyword, dict)
        ] if isinstance(keywords, list) else []
    )

    # Extract countries from authorships
    def get_countries(authorships):
        countries = set()
        if isinstance(authorships, list):
            for auth in authorships:
                auth_countries = auth.get("countries", [])
                if isinstance(auth_countries, list):
                    countries.update(auth_countries)
        return list(countries) if countries else []

    df["countries"] = df["authorships"].apply(get_countries)
    df["countries_count"] = df["countries"].apply(len)
    df["is_international"] = df["countries_count"] > 1

    # Extract venue info
    def get_venue_name(primary_location):
        if isinstance(primary_location, dict):
            source = primary_location.get("source")
            if isinstance(source, dict):
                return source.get("display_name", "Unknown")
        return "Unknown"

    df["venue_name"] = df.get(
        "primary_location", pd.Series(index=df.index)
    ).apply(get_venue_name)
    if "host_venue" in df.columns:
        legacy_venue = df["host_venue"].apply(
            lambda venue: venue.get("display_name", "Unknown")
            if isinstance(venue, dict) else "Unknown"
        )
        df["venue_name"] = df["venue_name"].where(
            df["venue_name"] != "Unknown", legacy_venue
        )

    # Extract type
    df["type"] = df.get("type", "Unknown")

    # Remove duplicates by id
    df = df.drop_duplicates(subset=["id"])

    # Reset index
    df = df.reset_index(drop=True)

    # Save processed data
    processed_path = Path(config["storage"]["processed_path"])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(processed_path, index=False)
    print(f"    Cleaned data saved to {processed_path}")

    return df