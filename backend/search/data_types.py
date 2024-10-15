from enum import Enum

from pydantic import BaseModel

from schema.idigbio.api import IDBRecordsQuerySchema


class Result(str, Enum):
    success = "success"
    error = "error"
    warning = "warning"


class Message(BaseModel):
    input: str
    rq: str | IDBRecordsQuerySchema
    result: Result
    message: str
