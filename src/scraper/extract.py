"""Data extraction module using requests and OpenAlex API."""

import json
import math
import time
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

import requests


def fetch_openalex(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetch data from OpenAlex API with pagination support.

    Args:
        config: Configuration dictionary with source parameters.

    Returns:
        List of raw records from OpenAlex.
    """
    source_cfg = config["source"]
    url = source_cfg["base_url"]
    params = source_cfg["params"].copy()
    headers = source_cfg["headers"]
    timeout = source_cfg.get("timeout", 30)
    max_retries = source_cfg.get("max_retries", 3)
    delay = source_cfg.get("delay_seconds", 1)
    date_range = source_cfg["publication_range"]
    first_year = date.fromisoformat(date_range["from_date"]).year
    last_year = date.fromisoformat(date_range["to_date"]).year
    max_records = source_cfg["max_sample_records"]
    page_size = min(200, params.get("per-page", 200))
    base_filter = params.pop("filter")
    params.pop("cursor", None)

    def request_json(request_params: Dict[str, Any], label: str) -> Dict[str, Any]:
        for attempt in range(max_retries + 1):
            try:
                started = perf_counter()
                response = requests.get(url, params=request_params, headers=headers, timeout=timeout)
                response.raise_for_status()
                payload = response.json()
                elapsed = perf_counter() - started
                print(f"    {label}: HTTP {response.status_code}; {elapsed:.2f}s")
                return payload
            except requests.RequestException as error:
                if attempt >= max_retries:
                    raise RuntimeError(
                        f"OpenAlex request failed for {label} after {max_retries} retries: {error}"
                    ) from error
                print(f"    Retry {attempt + 1}/{max_retries} for {label}: {error}")
                time.sleep(delay * 2)
        raise RuntimeError(f"OpenAlex request failed for {label} without a response")

    full_range_filter = (
        f"from_publication_date:{date_range['from_date']},"
        f"to_publication_date:{date_range['to_date']},{base_filter}"
    )
    grouped = request_json(
        {"filter": full_range_filter, "group_by": "publication_year", "per-page": 200},
        "Counting works by publication year",
    )
    year_counts = {
        int(item["key"]): int(item["count"])
        for item in grouped.get("group_by", [])
        if item.get("key") and str(item["key"]).isdigit()
    }
    total_available = sum(year_counts.values())
    if total_available == 0:
        raise RuntimeError("OpenAlex returned no works for the configured Tsinghua AI query")

    target_size = min(max_records, total_available)
    quotas = _allocate_year_quotas(year_counts, target_size, page_size)
    results: List[Dict[str, Any]] = []
    seen_ids = set()
    yearly_metadata: Dict[str, Dict[str, int]] = {}
    raw_path = Path(config["storage"]["raw_path"])
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    for year in sorted(quotas):
        quota = quotas[year]
        cursor = "*"
        collected = 0
        page = 0
        while collected < quota:
            page += 1
            request_params = params.copy()
            request_params.update({
                "filter": (
                    f"from_publication_date:{year}-01-01,"
                    f"to_publication_date:{year}-12-31,{base_filter}"
                ),
                "per-page": min(page_size, quota - collected),
                "cursor": cursor,
            })
            payload = request_json(request_params, f"Year {year}, page {page}")
            page_results = payload.get("results", [])
            added = 0
            for record in page_results:
                record_id = record.get("id")
                if record_id and record_id not in seen_ids:
                    results.append(record)
                    seen_ids.add(record_id)
                    added += 1
            collected += added
            print(
                f"    Year {year}: {added} new works "
                f"(year total: {collected}/{quota}; all years: {len(results)})"
            )
            with open(raw_path, "w", encoding="utf-8") as raw_file:
                json.dump(results, raw_file, ensure_ascii=False, indent=2)

            cursor = payload.get("meta", {}).get("next_cursor")
            if not page_results or not cursor or added == 0:
                break
            if collected < quota:
                time.sleep(delay)

        yearly_metadata[str(year)] = {
            "available": year_counts[year],
            "sampled": collected,
        }

    if len(results) != target_size:
        raise RuntimeError(
            f"OpenAlex sample incomplete: expected {target_size} unique works, "
            f"collected {len(results)}"
        )

    metadata = {
        "source": "OpenAlex Works API",
        "institution_id": config["scraping_rules"]["institution_id_openalex"],
        "ai_subfield_id": config["scraping_rules"]["ai_subfield_id_openalex"],
        "from_date": date_range["from_date"],
        "to_date": date_range["to_date"],
        "available_records": total_available,
        "sample_target": target_size,
        "collected_records": len(results),
        "yearly_counts": yearly_metadata,
    }
    metadata_path = Path(config["storage"]["metadata_path"])
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"    Raw data saved to {raw_path} ({len(results)} records)")
    print(f"    Collection metadata saved to {metadata_path}")
    return results


def _allocate_year_quotas(
    year_counts: Dict[int, int], target_size: int, max_per_page: int
) -> Dict[int, int]:
    """Allocate a capped sample proportionally across publication years."""
    quotas = {year: 0 for year in year_counts}
    remaining = target_size

    while remaining:
        active_years = [
            year for year, count in year_counts.items()
            if quotas[year] < min(count, max_per_page)
        ]
        if not active_years:
            raise RuntimeError("Could not allocate the requested sample across publication years")

        total_weight = sum(year_counts[year] for year in active_years)
        proposed = {
            year: remaining * year_counts[year] / total_weight
            for year in active_years
        }
        allocated = 0
        for year in active_years:
            capacity = min(year_counts[year], max_per_page) - quotas[year]
            amount = min(capacity, math.floor(proposed[year]))
            quotas[year] += amount
            allocated += amount
        remaining -= allocated

        if remaining:
            ordered_years = sorted(
                active_years,
                key=lambda year: proposed[year] - math.floor(proposed[year]),
                reverse=True,
            )
            for year in ordered_years:
                if not remaining:
                    break
                if quotas[year] < min(year_counts[year], max_per_page):
                    quotas[year] += 1
                    remaining -= 1

    return {year: quota for year, quota in quotas.items() if quota}


def fetch_data(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Main fetch function - routes to appropriate extractor based on config.

    Args:
        config: Configuration dictionary.

    Returns:
        List of raw records.
    """
    source_type = config["source"].get("type", "api")
    source_name = config["source"].get("name", "openalex")

    if source_type == "api" and source_name == "openalex":
        return fetch_openalex(config)
    else:
        raise ValueError(f"Unsupported source: {source_type}/{source_name}")