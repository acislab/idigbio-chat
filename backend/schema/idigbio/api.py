"""
This module provides pydantic schema used to craft and validate LLM responses.
"""
from datetime import date
from enum import Enum
from typing import Optional, List, Union, Literal

from pydantic import Field, BaseModel, EmailStr

from .fields import fields


class DateRange(BaseModel):
    type: Literal["range"]
    gte: date = Field(None, description="The start date of the range",
                      examples=["1900-3-14", "2024-01-01"])
    lte: date = Field(None, description="The end date of the range.",
                      examples=["1900-12-20", "2024-02-01"])


Date = Union[date, DateRange]


class ExistenceEnum(str, Enum):
    exists: "exists"
    missing: "missing"


class Existence(BaseModel):
    type: ExistenceEnum


String = Union[str, Existence]


class GeoPoint(BaseModel):
    """
    This schema represents a location on earth.
    """
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)


# Fields
field_names = [field['field_name'] for field in fields]

ScientificName = str


class IDBQuerySchema(BaseModel):
    """
    This schema represents the iDigBio Query Format.
    """
    associatedsequences: Optional[str] = None
    barcodevalue: Optional[str] = None
    basisofrecord: Optional[str] = None
    catalognumber: Optional[str] = None
    class_: Optional[str] = Field(default=None, alias='class')
    collectioncode: Optional[str] = None
    collectionid: Optional[str] = None
    collectionname: Optional[str] = None
    collector: Optional[str] = None
    commonname: Optional[str] = None
    continent: Optional[str] = None
    country: Optional[str] = None
    county: Optional[str] = None
    datecollected: Optional[Date] = None
    datemodified: Optional[Date] = None
    earliestperiodorlowestsystem: Optional[str] = None
    etag: Optional[str] = None
    eventdate: Optional[Date] = None
    family: Optional[str] = None
    fieldnumber: Optional[str] = None
    genus: Optional[str] = None
    geopoint: Optional[GeoPoint] = None
    hasImage: Optional[bool] = None
    highertaxon: Optional[str] = None
    infraspecificepithet: Optional[str] = None
    institutioncode: Optional[str] = None
    institutionid: Optional[str] = None
    institutionname: Optional[str] = None
    kingdom: Optional[str] = None
    latestperiodorhighestsystem: Optional[str] = None
    locality: Optional[str] = None
    maxdepth: Optional[float] = None
    maxelevation: Optional[float] = None
    mediarecords: Optional[str] = None
    mindepth: Optional[float] = None
    minelevation: Optional[float] = None
    municipality: Optional[str] = None
    occurrenceid: Optional[str] = None
    order: Optional[str] = None
    phylum: Optional[str] = None
    recordids: Optional[str] = None
    recordnumber: Optional[str] = None
    recordset: Optional[str] = None
    scientificname: Optional[Union[ScientificName, List[ScientificName]]] = None
    specificepithet: Optional[str] = None
    stateprovince: Optional[Union[str, List[str]]] = None
    typestatus: Optional[str] = None
    uuid: Optional[str] = None
    verbatimeventdate: Optional[str] = None
    verbatimlocality: Optional[str] = None
    version: Optional[int] = None
    waterbody: Optional[str] = None

    class Config:
        json_encoders = {
            date: date.isoformat
        }


class IDigBioRecordsApiParameters(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query. 
    """
    rq: IDBQuerySchema = Field(...,
                               description="This is the iDigBio Query format and should contain the query generated "
                                           "from the user's plain text input.")
    limit: Optional[int] = Field(None,
                                 description="The maximum number of records to return. Only set this field if the "
                                             "user specifically requests a record limit.")


class IDigBioSummaryApiParameters(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query.
    """
    rq: IDBQuerySchema = Field(...,
                               description="This is the iDigBio Query format and should contain the query generated "
                                           "from the user's plain text input.")
    top_fields: Optional[str] = Field(...,
                                      description="The field to break down record counts by. Defaults to "
                                                  "\"scientificname\". For example, if top_fields is \"country\", "
                                                  "the iDigBio API will find the 10 countries with the most records "
                                                  "matching the search parameters. Only one top field may be "
                                                  "specified.")
    count: Optional[int] = Field(None,
                                 description="The maximum number of categories to use for the counts breakdown. For "
                                             "example, to find 10 species, set \"count\" to 10.")


class IDigBioDownloadApiParameters(IDigBioRecordsApiParameters):
    """
    This schema represents the output containing the LLM-generated iDigBio query.
    """
    email: EmailStr = Field(...,
                            description="The email address to send the results of the search to. The email will "
                                        "contain a link to download the results packaged as a DarwinCore Archive zip "
                                        "file.")
