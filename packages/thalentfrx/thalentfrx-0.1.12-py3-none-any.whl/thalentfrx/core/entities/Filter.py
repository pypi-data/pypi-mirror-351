from enum import Enum

from pydantic import BaseModel


class OperatorTypes(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="

    LIKE = "like"
    IN = "in"

    BETWEEN = "between"
    NOT_IN = "not_in"
    START_WITH = "start_with"
    END_WITH = "end_with"
    CONTAINS = "contains"


class Filter(BaseModel):
    property: str
    operator: OperatorTypes
    value: str
