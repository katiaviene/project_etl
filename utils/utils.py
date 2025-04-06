import pandas as pd


def get_column(x, key):
    """
    Extracts the value corresponding to a given key from a dictionary, or returns an empty string if the key doesn't exist.

    Args:
        x (any): The input value, expected to be a dictionary.
        key (str): The key to extract the value for.

    Returns:
        str: The value corresponding to the key, or an empty string if the key is not found.
    """
    return x.get(key,'') if isinstance(x, dict) else ''

def set_column(df, keys):
    """
    Adds new columns to the dataframe by extracting values from the 'data' column.

    This function iterates over the provided keys, applies the `get_column` function to extract the values for each key from the 'data' column,
    and adds the extracted values as new columns in the dataframe. If the key is 'date', the date values are formatted to 'YYYY-MM-DD' format.

    Args:
        df (pd.DataFrame): The dataframe to modify, which should contain a 'data' column.
        keys (list of str): The list of keys to extract from the 'data' column and create new columns for.

    Returns:
        pd.DataFrame: The modified dataframe containing the new columns for each key.
    """
    for key in keys:
        df[key] = df['data'].apply(lambda x: get_column(x, key))
        if key == 'date':
            df[key] = pd.to_datetime(df[key]).dt.strftime('%Y-%m-%d')
    return df[keys]