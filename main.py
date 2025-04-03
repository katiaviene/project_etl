import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
from utils import utils
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from sqlalchemy import create_engine

load_dotenv()
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
keyword = ','.join(["vpn", "antivirus", "ad blocker", "password manager"])
region = 'US'
date_range = " ".join([(date.today()-timedelta(days=180)).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d') ])
keys = ['date', 'query', 'value']

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

    
def normalize_data(results):
    df = pd.json_normalize(results)
    print(df.columns)
    df_last = df[['interest_over_time.timeline_data',  'interest_over_time.averages']]
    df_exploded = df_last.explode(['interest_over_time.timeline_data']).explode(['interest_over_time.averages'])
    df_exploded['data'] = df_exploded.apply(
    lambda row: {**row['interest_over_time.timeline_data'], **row['interest_over_time.averages']}, axis=1
        )
    return df_exploded

def write_data(df):
    engine = create_engine(DATABASE_URL)
    df.to_sql('search_data', con=engine, if_exists='replace', index=False)


def predict(df):
    df['date'] = pd.to_datetime(df['date'])
    df['date_ordinal'] = df['date'].map(lambda x: x.toordinal())

    # Define features (X) and target (y)
    X = df[['date_ordinal', 'value']]
    y = df['value']

    # Train regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next week's searches
    next_week_date = (df['date'].max() + pd.Timedelta(days=7)).toordinal()
    next_week_features = np.array([[next_week_date, 0.5, 3000]])  # Example future values
    predicted_value = model.predict(next_week_features)

    print(f"Predicted search volume for next week: {predicted_value[0]:.2f}")

if __name__ == '__main__':
    parameters = get_parameters(api_key=API_KEY, keywords=keyword, date_range=date_range, region=region)
    data_json = get_data(parameters)
    df = normalize_data(data_json)
    df = utils.set_column(df, keys) 
    # predict(df)
    print(df)
    write_data(df)