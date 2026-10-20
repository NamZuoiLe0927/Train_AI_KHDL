# Tsinghua University AI Research Data Pipeline

Complete data pipeline for collecting, cleaning, analyzing, and visualizing AI research publications from Tsinghua University (清华大学) using OpenAlex API.

## 📁 Project Structure

```
TrainAI/
├── config/
│   └── config.yaml           # Configuration file
├── data/
│   ├── raw/                  # Raw JSON data from API
│   ├── processed/            # Cleaned parquet files
│   └── final/                # Feature-engineered data
├── notebooks/
│   └── analysis.ipynb        # EDA notebook
├── outputs/
│   ├── figures/              # Static charts (PNG) + Interactive (HTML)
│   └── reports/              # Dashboard HTML
├── reports/                  # Final reports
├── src/
│   ├── main.py               # Main pipeline entry point
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── extract.py        # Data extraction from OpenAlex
│   ├── cleaner/
│   │   ├── __init__.py
│   │   └── clean.py          # Data cleaning & normalization
│   ├── feature_engineering/
│   │   ├── __init__.py
│   │   └── features.py       # Feature creation
│   ├── reporting.py          # CSV exports and HTML reports
│   └── visualization/
│       ├── __init__.py
│       └── visualize.py      # Charts & dashboard creation
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Full Pipeline

```bash
python src/main.py
```

This executes:
1. **Extract** - Fetch data from OpenAlex API
2. **Clean** - Normalize, handle missing values, remove duplicates
3. **Feature Engineering** - Create derived features
4. **Visualize** - Generate 6+ chart groups + 3+ interactive charts

The OpenAlex query selects works affiliated with Tsinghua University
(`I99065089`) and having a topic in the Artificial Intelligence subfield
(`1702`), published from 2015-01-01 through the configured current cutoff.
The pipeline first counts matching works by year, then takes a proportional
sample of up to 1,200 works (no more than 200 from each year) so the sample
covers the full requested period. This API-ordered sample is not random.

### 3. Run Jupyter Notebook

```bash
jupyter notebook notebooks/analysis.ipynb
```

## 📊 Outputs

### Data and Visualization Files

Raw JSON, collection metadata, cleaned and feature-engineered Parquet files,
charts, dashboard, CSV tables, data-quality report, and storytelling report
are written to the standard `data/` and `outputs/` locations. Running the
pipeline replaces the prior generated outputs at those paths.

Static charts include histogram, boxplot, violin, line, area, scatter with
regression, correlation heatmap, research-area treemap alternative, word cloud,
and a co-author network. Three interactive Plotly charts and a combined
dashboard are also generated.

The data-quality report documents missing metadata and the sample limitations.
Tables for research groups, LLM models, datasets, open-source projects, and
rankings are emitted with their required schemas but remain empty until
verified source-specific data is collected; the pipeline does not fabricate
these records.

## ⚙️ Configuration

Edit `config/config.yaml` to customize:
- API parameters (date range, page size)
- Storage paths
- Visualization settings
- Legal compliance flags

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for full list

## 📝 License

Educational/Research purposes only. Respects OpenAlex Terms of Service.