import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv
import yaml
import os
from utils import utils
from datetime import date, timedelta
import numpy as np
from sqlalchemy import create_engine
from validation import SearchTrendModel
from pydantic import ValidationError
from prediction import predict_next_week

load_dotenv()
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_parameters(api_key, keywords, date_range=None, region=None):
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

def normalize_data(results, fields):
    df = pd.json_normalize(results)
    df_last = df[fields]
    df_exploded = df_last.explode(fields[0])
    df_exploded['data'] = df_exploded[fields[0]].apply(lambda x: x.get('values'))
    dff = df_exploded.explode('data')
    dff['data'] = dff.apply(lambda x: {**x['data'], 'date': x[fields[0]].get('date')} if isinstance(x['data'], dict) else x['data'], axis=1)
    return dff

def validate_df(df):
    valid_rows = []
    errors = []
    for idx, row in df.iterrows():
        try:
            validated = SearchTrendModel(**row.to_dict())
            valid_rows.append(validated)
        except ValidationError as e:
            errors.append((idx, e))
    return valid_rows, errors

def write_data(df, target_table, load="replace"):
    engine = create_engine(DATABASE_URL)
    df.to_sql(target_table, con=engine, if_exists=load, index=False)
    print("Data loaded")

if __name__ == '__main__':
    config = load_config("api_config.yml")
    for api in config.get("api", []):
        print(f'{api.get("name", "unknown")} loading')
        print(f'target:{api.get("target")}')
        date_range = " ".join([(date.today()-timedelta(days=api.get("parameters", {}).get("period", 0))).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d') ])

        parameters = get_parameters( api_key=API_KEY,
                                     keywords=', '.join(api.get("parameters", {}).get("keywords", [])),
                                     date_range=date_range,
                                     region=api.get("parameters", {}).get("region", None)
                                    )
        data_json = get_data(parameters)
        df = normalize_data(data_json, api.get("fields", []))
        df = utils.set_column(df, api.get("target_columns", [])) 
        print(f'Data sample:\n {df.sort_values(by="date", ascending=False).head()}')
        valid, errs = validate_df(df)
        print(f"Valid:{len(valid)}, error: {len(errs)}")
        if not errs:
            write_data(df=df, target_table=api.get("target", ""), load=api.get("load", "replace") )
            "Data is loaded"
        print(f'Predicted values of searches:\n{predict_next_week(df, api.get("predict_period", 1))}')