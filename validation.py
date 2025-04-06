from pydantic import BaseModel, field_validator
from typing import Union
from datetime import date


class SearchTrendModel(BaseModel):
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
