import pandas as pd


def get_column(x, key):
    return x.get(key,'') if isinstance(x, dict) else ''

def set_column(df, keys):
    for key in keys:
        df[key] = df['data'].apply(lambda x: get_column(x, key))
        if key == 'date':
            df[key] = pd.to_datetime(df[key]).dt.strftime('%Y-%m-%d')
    return df[keys]