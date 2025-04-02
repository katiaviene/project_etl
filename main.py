import requests
import pandas as pd
from serpapi import GoogleSearch



# Keyword to search
keyword = ','.join(["vpn", "antivirus", "ad blocker", "password manager"])


# API Endpoint
url = f"https://serpapi.com/search?engine=google_trends"
params = {
  "engine": "google_trends",
  "q": keyword,
  "data_type": "TIMESERIES",
  "api_key": API_KEY,
  "geo": "US",
  "date": "2024-12-01 2025-04-02"
}

# search = GoogleSearch(params)
# results = search.get_dict()
print(results)

