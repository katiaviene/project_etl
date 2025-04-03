def get_column(x, key):
    return x.get(key,'') if isinstance(x, dict) else ''

def set_column(df, keys):
    for key in keys:
        df[key] = df['data'].apply(get_column(key))