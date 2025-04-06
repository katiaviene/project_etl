import pytest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import yaml
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from validation import SearchTrendModel
from prediction import predict_next_week
from dotenv import load_dotenv
from main import load_config, get_parameters, get_data, normalize_data, validate_df, write_data


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
    return {
        'interest_over_time': {
            'timeline_data': [{'date': '2024-10-08', 'values': [{"query":"cat", "value": 8}]}, {'date': '2024-10-09', 'values': {"query":"cat", "value": 9}}],
        }
    }

@patch('main.GoogleSearch')
@patch('main.os.getenv')
def test_get_parameters(mock_getenv, mock_GoogleSearch, mock_config):
    """Test get_parameters function"""
    mock_getenv.return_value = 'test_api_key'
    parameters = get_parameters(api_key='test_api_key', keywords='test_keyword', date_range='2024-01-01,2024-02-01', region='US')

    assert parameters['engine'] == 'google_trends'
    assert parameters['q'] == 'test_keyword'
    assert parameters['api_key'] == 'test_api_key'
    assert parameters['geo'] == 'US'


@patch('main.GoogleSearch')
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
    assert 'data' in df.columns  

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

