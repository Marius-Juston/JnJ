from typing import Annotated

from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic.v1 import validator

def validate_int(x):
    return x or 0

MyInteger =  Annotated[int, validate_int]

class TimeEstimate(BaseModel):
    """The estimated time it will take to complete an action"""
    days: MyInteger = Field(..., description="The number of days it is estimated that the action will take to complete")
    hours: MyInteger = Field(..., description="The number of hours it is estimated that the action will take to complete")
    minutes: MyInteger = Field(..., description="The number of minutes it is estimated that the action will take to complete")
    seconds: MyInteger = Field(..., description="The number of seconds it is estimated that the action will take to complete")
