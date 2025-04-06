# project_etl # Google Trends Timeseries Collector

This project uses the [SerpApi Google Trends API](https://serpapi.com/google-trends-api) to collect and normalize trend data for a set of keywords over a configurable time period and geographic region. The normalized data can be stored in a database and optionally used for search volume prediction.

## Features

- Fetch Google Trends data using SerpApi
- Fully configurable via a YAML file
- Normalize API results into a flat structure for analysis or storage
- Predict future search volume using linear regression
- Supports PostgreSQL (or any SQLAlchemy-compatible DB)

---

## Requirements

- Python 3.8+
- A [SerpApi API Key](https://serpapi.com/)
- A PostgreSQL database URL (optional, for writing results)

### Python Dependencies

Install via pip:

```bash
pip install -r requirements.txt
