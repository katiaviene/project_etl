from sklearn.linear_model import LinearRegression
import pandas as pd

def predict_next_week(df, days):
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