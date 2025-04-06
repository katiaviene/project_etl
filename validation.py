from pydantic import BaseModel, field_validator
from typing import Union
from datetime import date


class SearchTrendModel(BaseModel):
    """
    A Pydantic model for validating search trend data.

    This model is used to validate the structure of search trend data, ensuring that:
    - The 'date' field is a valid date.
    - The 'query' field is a non-empty string.
    - The 'value' field is a non-negative number (either an integer or float).

    Attributes:
        date (date): The date of the search trend.
        query (str): The search query string.
        value (Union[int, float]): The number of searches for the query on the given date.

    Validators:
        query_not_null (field_validator): Ensures that the 'query' field is not empty or whitespace.
        value_positive (field_validator): Ensures that the 'value' field is a non-negative number.
    """
    date: date
    query: str
    value: Union[int, float]

    @field_validator('query')
    def query_not_null(cls, v):
        if not v.strip():
            raise ValueError("query must not be empty")
        return v

    @field_validator('value')
    def value_positive(cls, v):
        if v < 0:
            raise ValueError("value must be non-negative")
        return v
