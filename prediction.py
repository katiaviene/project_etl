from sklearn.linear_model import LinearRegression
import pandas as pd

def predict_next_week(df, days):
    """
    Predicts the number of searches for the next week based on historical search data.

    This function performs linear regression on the historical search data to predict the number of searches
    for the specified number of days (next week). It uses both the ordinal date and the day of the week as features
    to train the model and generate predictions.

    Args:
        df (pd.DataFrame): A DataFrame containing historical search data with columns `date`, `query`, and `value`.
        days (int): The number of days for which to generate predictions (i.e., how many days into the future).

    Returns:
        pd.DataFrame: A DataFrame with predicted search values for the next `days` number of days. 
                      It includes columns `query`, `date`, and `predicted_value`.
    """
    df['date'] = pd.to_datetime(df['date'])
    predictions = []

    for query, group in df.groupby('query'):
        group = group.sort_values('date')

        group['date_ordinal'] = group['date'].map(lambda d: d.toordinal())
        group['day_of_week'] = group['date'].dt.dayofweek

        X = group[['date_ordinal', 'day_of_week']]
        y = group['value']
        
        if len(X) < 2:
            continue

        model = LinearRegression()
        model.fit(X, y)

        next_week_dates = pd.date_range(group['date'].max() + pd.Timedelta(days=1), periods=days, freq='D')
        next_week_ordinal = next_week_dates.map(lambda d: d.toordinal())
        next_week_day_of_week = next_week_dates.dayofweek

        X_next = pd.DataFrame({
            'date_ordinal': next_week_ordinal,
            'day_of_week': next_week_day_of_week
        })
        
        predicted_values = model.predict(X_next)
        for i in range(len(next_week_dates)):
            predictions.append({
                'query': query,
                'date': next_week_dates[i],
                'predicted_value': round(predicted_values[i])
            })

    predictions_df = pd.DataFrame(predictions)
    return predictions_df