"""
This module provides pydantic schema used to craft and validate LLM responses.
"""
from datetime import date
from enum import Enum
from typing import Optional, List, Union, Literal

from pydantic import Field, BaseModel, EmailStr, field_validator, ValidationError
from pydantic_core import PydanticCustomError

from .fields import fields


class DateRange(BaseModel):
    type: Literal["range"]
    gte: Optional[date] = Field(None, description="The start date of the range",
                                examples=["1900-3-14", "2024-01-01"])
    lte: Optional[date] = Field(None, description="The end date of the range.",
                                examples=["1900-12-20", "2024-02-01"])


class Existence(BaseModel):
    type: Literal["exists", "missing"]


Date = Union[date, DateRange, Existence]
String = Union[str, Existence]
Bool = Union[bool, Existence]
Float = Union[bool, Existence]
Int = Union[int, Existence]


class GeoPoint(BaseModel):
    """
    This schema represents a location on earth.
    """
    latitude: Optional[Float] = Field(None)
    longitude: Optional[Float] = Field(None)

    @field_validator('latitude', mode='after')
    @classmethod
    def validate_latitude(cls, v):
        if v is None:
            return v
        if not (-90 <= v <= 90):
            raise PydanticCustomError(
                "geopoint_range_error",
                "Error: Invalid latitude value: {latitude} is not in range [-90, +90]",
                dict(latitude=v, terminal=True)
            )
        return v

    @field_validator('longitude', mode='after')
    @classmethod
    def validate_longitude(cls, v):
        if v is None:
            return v
        if not (-180 <= v <= 180):
            raise PydanticCustomError(
                "geopoint_range_error",
                "Error: Invalid latitude value: {longitude} is not in range [-180, +180]",
                dict(longitude=v, terminal=True)
            )
        return v


# Fields
field_names = [field['field_name'] for field in fields]


class IDBRecordsQuerySchema(BaseModel):
    """
    This schema represents the iDigBio Record Query Format.
    """
    associatedsequences: Optional[String] = None
    barcodevalue: Optional[String] = None
    basisofrecord: Optional[String] = None
    catalognumber: Optional[String] = None
    class_: Optional[String] = Field(None, alias='class')
    collectioncode: Optional[String] = None
    collectionid: Optional[String] = None
    collectionname: Optional[String] = None
    collector: Optional[String] = None
    commonname: Optional[String] = Field(None,
                                         description="Common name for a specific species. Do not use for taxonomic "
                                                     "groups like \"birds\" or \"mammals\"")
    continent: Optional[String] = None
    country: Optional[String] = Field(None,
                                      description="Full, accepted country name. For example 'Canada' instead of CAD.")
    county: Optional[String] = None
    datecollected: Optional[Date] = None
    datemodified: Optional[Date] = None
    earliestperiodorlowestsystem: Optional[String] = None
    etag: Optional[String] = None
    eventdate: Optional[Date] = None
    family: Optional[String] = None
    fieldnumber: Optional[String] = None
    genus: Optional[String] = None
    geopoint: Optional[GeoPoint] = None
    hasImage: Optional[Bool] = None
    highertaxon: Optional[String] = None
    infraspecificepithet: Optional[String] = None
    institutioncode: Optional[String] = None
    institutionid: Optional[String] = None
    institutionname: Optional[String] = None
    kingdom: Optional[String] = None
    latestperiodorhighestsystem: Optional[String] = None
    locality: Optional[String] = None
    maxdepth: Optional[Float] = None
    maxelevation: Optional[Float] = None
    mediarecords: Optional[String] = None
    mindepth: Optional[Float] = None
    minelevation: Optional[Float] = None
    municipality: Optional[String] = None
    occurrenceid: Optional[String] = None
    order: Optional[String] = None
    phylum: Optional[String] = None
    recordids: Optional[String] = None
    recordnumber: Optional[String] = None
    recordset: Optional[String] = None
    scientificname: Optional[Union[String, List[str]]] = None
    specificepithet: Optional[String] = None
    stateprovince: Optional[Union[String, List[str]]] = None
    typestatus: Optional[String] = None
    uuid: Optional[String] = None
    verbatimeventdate: Optional[String] = None
    verbatimlocality: Optional[String] = None
    version: Optional[Int] = None
    waterbody: Optional[String] = None

    class Config:
        json_encoders = {
            date: date.isoformat
        }


class IDBMediaQuerySchema(BaseModel):
    """
    This schema represents the iDigBio Media Query Format.
    """
    uuid: Optional[String] = None
    datemodified: Optional[Date] = Field(None, description="The \"datemodified\" field in the original media record")
    modified: Optional[Date] = Field(None,
                                     description="Last time the media record changed in iDigBio, whether the original "
                                                 "record or iDigBio's metadata")
    etag: Optional[String] = None
    version: Optional[Int] = None
    recordset: Optional[String] = Field(None, description="The record set that the media record is a part of")
    records: Optional[String] = Field(None, description="UUIDs for records that are associated with the media record")
    hasSpecimen: Optional[Bool] = Field(None,
                                        description="Whether the media record is associated with a specific species "
                                                    "occurrence record")

    class Config:
        json_encoders = {
            date: date.isoformat
        }


class IDigBioRecordsApiParameters(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query. 
    """
    rq: IDBRecordsQuerySchema = Field(...,
                                      description="Search criteria for species occurrence records in iDigBio")
    limit: Optional[int] = Field(None,
                                 description="The maximum number of records to return")


class IDigBioSummaryApiParameters(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query.
    """
    rq: Optional[IDBRecordsQuerySchema] = Field(None,
                                                description="This is the iDigBio Query format and should contain the "
                                                            "query "
                                                            "generated from the user's plain text input.")
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


class IDigBioMediaApiParameters(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query.
    """
    mq: Optional[IDBMediaQuerySchema] = Field(None,
                                              description="Search criteria for media and media records")
    rq: Optional[IDBRecordsQuerySchema] = Field(None,
                                                description="Search criteria for species occurrence records")
    limit: Optional[int] = Field(None,
                                 description="The maximum number of records to return")
