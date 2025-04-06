import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import yaml
import os
from ..validation import SearchTrendModel
from ..prediction import predict_next_week
from dotenv import load_dotenv
from ..main import load_config, get_parameters, get_data, normalize_data, validate_df, write_data


@pytest.fixture
def mock_config():
    """Mock the config loading."""
    return {
        'api': [{
            'name': 'API1',
            'target': 'table1',
            'parameters': {
                'keywords': ['keyword1', 'keyword2'],
                'period': 30,
                'region': 'US'
            },
            'fields': ['interest_over_time.timeline_data'],
            'target_columns': ['column1', 'column2'],
            'predict_period': 1
        }]
    }

@pytest.fixture
def mock_api_response():
    """Mock the API response for get_data"""
    return {
        'interest_over_time': {
            'timeline_data': [{'date': '2024-10-08', 'value': 5}, {'date': '2024-10-09', 'value': 7}],
            'averages': [6, 6.5]
        }
    }

@patch('your_module.GoogleSearch')
@patch('your_module.os.getenv')
def test_get_parameters(mock_getenv, mock_GoogleSearch, mock_config):
    """Test get_parameters function"""
    mock_getenv.return_value = 'test_api_key'
    parameters = get_parameters(api_key='test_api_key', keywords='test_keyword', date_range='2024-01-01,2024-02-01', region='US')

    assert parameters['engine'] == 'google_trends'
    assert parameters['q'] == 'test_keyword'
    assert parameters['api_key'] == 'test_api_key'
    assert parameters['geo'] == 'US'

def test_load_config(mock_config):
    """Test config loading"""
    with patch('builtins.open', MagicMock(return_value=mock_config)):
        config = load_config('mock_config.yml')
        assert config == mock_config

@patch('your_module.GoogleSearch')
def test_get_data(mock_GoogleSearch, mock_api_response):
    """Test the get_data function"""
    mock_GoogleSearch.return_value.get_dict.return_value = mock_api_response
    params = {"engine": "google_trends", "q": "test_keyword"}
    results = get_data(params)
    assert 'interest_over_time' in results
    assert len(results['interest_over_time']['timeline_data']) == 2

def test_normalize_data(mock_api_response):
    """Test the normalize_data function"""
    df = normalize_data(mock_api_response, fields=['interest_over_time.timeline_data'])
    assert df.shape[0] == 2  # Expected two rows after normalization and exploding
    assert 'date' in df.columns  # Ensure the date column was added

def test_validate_df():
    """Test the validate_df function with valid data"""
    valid_data = [{
        'date': '2024-10-08',
        'value': 5,
        'query': 'keyword1'
    }]
    df = pd.DataFrame(valid_data)
    valid_rows, errors = validate_df(df)
    assert len(valid_rows) == 1
    assert len(errors) == 0

@patch('your_module.predict_next_week')
def test_predict_next_week(mock_predict_next_week, mock_api_response):
    """Test the prediction functionality"""
    df = pd.DataFrame(mock_api_response['interest_over_time']['timeline_data'])
    mock_predict_next_week.return_value = {"keyword1": 10}  # Mocked predicted value
    predicted = predict_next_week(df, predict_period=1)
    assert predicted == {"keyword1": 10}

def test_write_data():
    """Test the write_data function"""
    with patch('your_module.create_engine') as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        df = pd.DataFrame({'column1': [1, 2], 'column2': [3, 4]})
        write_data(df, target_table='test_table', load='replace')
        mock_create_engine.assert_called_once_with(os.getenv('DATABASE_URL'))
        mock_engine.to_sql.assert_called_once_with('test_table', con=mock_engine, if_exists='replace', index=False)
