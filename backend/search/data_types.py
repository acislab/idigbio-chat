from enum import Enum

from pydantic import BaseModel

from schema.idigbio.records_api import IDBQuerySchema


class Result(str, Enum):
    success = "success"
    error = "error"
    warning = "warning"


class Message(BaseModel):
    input: str
    rq: str | IDBQuerySchema
    result: Result
    message: str
