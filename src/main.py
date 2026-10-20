#!/usr/bin/env python3
"""
Main entry point for the Data Collection & Analysis Pipeline.
Runs the complete ETL process: Extract -> Clean -> Feature Engineering -> Visualize
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scraper.extract import fetch_data
from cleaner.clean import clean_data
from feature_engineering.features import create_features
from reporting import create_reports
from visualization.visualize import create_visualizations, create_dashboard


def load_config():
    """Load configuration from YAML file."""
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    """Run the complete pipeline."""
    print("=" * 60)
    print("DATA PIPELINE: Extract -> Clean -> Features -> Visualize -> Reports")
    print("=" * 60)

    config = load_config()
    print("    Outputs use the project's standard data/, outputs/figures/, and outputs/reports/ paths")

    # Step 1: Extract
    print("\n[1/5] Extracting data...")
    raw_data = fetch_data(config)
    print(f"    Extracted {len(raw_data)} records")

    # Step 2: Clean
    print("\n[2/5] Cleaning data...")
    df_clean = clean_data(raw_data, config)
    print(f"    Cleaned shape: {df_clean.shape}")

    # Step 3: Feature Engineering
    print("\n[3/5] Creating features...")
    df_final = create_features(df_clean, config)
    print(f"    Final shape: {df_final.shape}")

    # Step 4: Visualize
    print("\n[4/5] Creating visualizations...")
    create_visualizations(df_final, config)
    create_dashboard(df_final, config)
    print(f"    Visualizations saved to {config['storage']['figure_dir']}")

    print("\n[5/5] Exporting reports and tabular datasets...")
    create_reports(df_final, config)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()