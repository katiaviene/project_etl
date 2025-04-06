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
    """
    Loads configuration data from a YAML file.

    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        dict: The configuration data parsed from the YAML file.

    Raises:
        FileNotFoundError: If the specified config_file does not exist.
        yaml.YAMLError: If the YAML file is improperly formatted.
    """
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_parameters(api_key, keywords, date_range=None, region=None):
    """
    Constructs a dictionary of parameters for a Google Trends API request.

    Args:
        api_key (str): The API key for accessing the Google Trends API.
        keywords (str): A comma-separated string of keywords to query for trends.
        date_range (str, optional): The date range for the trend data, in 'YYYY-MM-DD' format. Defaults to None.
        region (str, optional): The region for the trends data. Defaults to None.

    Returns:
        dict: A dictionary containing the parameters needed for the Google Trends API request.
    """
    return {
            "engine": "google_trends",
            "q": keywords,
            "data_type": "TIMESERIES",
            "api_key": api_key,
            "geo": region,
            "date": date_range
            }

def get_data(params):
    """
    Retrieves data from the Google Trends API using the provided parameters.

    Args:
        params (dict): A dictionary of parameters required for the Google Trends API request.
            This typically includes keys such as 'engine', 'q', 'data_type', 'api_key', 'geo', and 'date'.

    Returns:
        dict: The data returned by the Google Trends API, usually in the form of a dictionary with trend information.
    """
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

def normalize_data(results, fields):
    """
    Normalizes and processes the input data from the Google Trends API into a Pandas DataFrame format.

    This function takes raw data (as a dictionary) from the Google Trends API, normalizes it into a structured
    DataFrame, and processes the nested fields to make the data more accessible for analysis.

    Args:
        results (dict): The raw data returned by the Google Trends API, typically containing trend data in nested structures.
        fields (list): A list of strings specifying the fields to extract from the raw results. The first field is assumed
                       to contain nested lists that will be exploded into separate rows.

    Returns:
        pd.DataFrame: A normalized DataFrame containing the processed data, with each row representing a separate value
                      from the nested structures, including the query's date.
    """
    df = pd.json_normalize(results)
    df = df[fields]
    df_exploded = df.explode(fields[0])
    df_exploded['data'] = df_exploded[fields[0]].apply(lambda x: x.get('values'))
    df_result = df_exploded.explode('data')
    df_result['data'] = df_result.apply(lambda x: {**x['data'], 'date': x[fields[0]].get('date')} if isinstance(x['data'], dict) else x['data'], axis=1)
    return df_result

def validate_df(df):
    """
    Validates each row of the input DataFrame using the SearchTrendModel.

    This function iterates through each row of the provided DataFrame, attempts to validate it using the
    SearchTrendModel, and collects the valid rows and any validation errors. Rows that pass validation are
    stored in the `valid_rows` list, and rows that raise a ValidationError are recorded in the `errors` list.

    Args:
        df (pd.DataFrame): A DataFrame where each row contains the data to be validated using the SearchTrendModel.

    Returns:
        tuple: A tuple containing:
            - valid_rows (list): A list of validated rows as instances of the SearchTrendModel.
            - errors (list): A list of tuples where each tuple contains the index of the row and the associated
                              ValidationError for rows that failed validation.
    """
    valid_rows = []
    errors = []
    for idx, row in df.iterrows():
        try:
            validated = SearchTrendModel(**row.to_dict())
            valid_rows.append(validated)
        except ValidationError as e:
            errors.append((idx, e))
    print(f"Valid:{len(valid_rows)}, error: {len(errors)}")
    return valid_rows, errors

def write_data(df, target_table, load="replace"):
    """
    Writes the provided DataFrame to a SQL database table.

    This function establishes a connection to the SQL database using the `DATABASE_URL` environment variable
    and writes the given DataFrame to the specified target table. The `if_exists` parameter defines what
    happens if the table already exists.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be written to the database.
        target_table (str): The name of the target table in the database where the DataFrame will be written.
        load (str, optional): The method for handling an existing table. Defaults to "replace", which will
                              drop and recreate the table. Other options include "append" to append data
                              to an existing table. (Optional)

    Returns:
        None
    """
    engine = create_engine(DATABASE_URL)
    df.to_sql(target_table, con=engine, if_exists=load, index=False)
    print("Data loaded")

if __name__ == '__main__':
    
    config = load_config("api_config.yml")
    for api in config.get("api", []):
        
        print(f'{api.get("name", "unknown")} loading')
        print(f'target:{api.get("target")}')
        
        date_range = " ".join([(date.today()-timedelta(days=api.get("parameters", {}).get("period", 0))).strftime('%Y-%m-%d'), date.today().strftime('%Y-%m-%d') ])

        parameters = get_parameters(
            api_key=API_KEY,
            keywords=', '.join(api.get("parameters", {}).get("keywords", [])),
            date_range=date_range,
            region=api.get("parameters", {}).get("region", None)
        )

        data_json = get_data(parameters)
        df = normalize_data(data_json, api.get("fields", []))
        df = utils.set_column(df, api.get("target_columns", [])) 
        
        print(f'Data sample:\n {df.sort_values(by="date", ascending=False).head()}')
        
        valid, errs = validate_df(df)
        if not errs:
            write_data(df=df, target_table=api.get("target", ""), load=api.get("load", "replace") )
        else: 
            print("Data is not complient with validation rules")
        print(f'Predicted values of searches:\n{predict_next_week(df, api.get("predict_period", 1))}')