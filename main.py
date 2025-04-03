import requests
import pandas as pd
from serpapi import GoogleSearch
import json
import ast
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')
keyword = ','.join(["vpn", "antivirus", "ad blocker", "password manager"])
region = 'US'
date_range = "2024-12-01 2025-04-02"


def get_parameters(api_key, keywords, date_range, region):
    return {
            "engine": "google_trends",
            "q": keywords,
            "data_type": "TIMESERIES",
            "api_key": api_key,
            "geo": region,
            "date": date_range
            }

def get_data(params):

    search = GoogleSearch(params)
    results = search.get_dict()
    return results

def get_column(x, key):
    return x.get(key,'') if isinstance(x, dict) else ''

def set_column(df, keys):
    for key in keys:
        df[key] = df[''].apply(get_column(key))
    
    
def normalize_data(results):
    df = pd.json_normalize(results)
    print(df.columns)



    df_last = df[['interest_over_time.timeline_data',  'interest_over_time.averages']]
    print(df_last)
    df_exploded = df_last.explode(['interest_over_time.timeline_data']).explode(['interest_over_time.averages'])


    df_exploded['date'] = df_exploded['interest_over_time.timeline_data'].apply()
    df_exploded['query'] =  df_exploded['interest_over_time.averages'].apply(lambda x: x.get('query', '') if isinstance(x, dict) else '')
    df_exploded['value'] =  df_exploded['interest_over_time.averages'].apply(lambda x: x.get('value', '') if isinstance(x, dict) else '')
    print(df_exploded[['date', 'query', 'value']])