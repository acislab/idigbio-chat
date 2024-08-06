"""
This module provides pydantic schema used to craft and validate LLM responses.
"""

from pydantic import Field, BaseModel, model_validator, ValidationInfo
from typing import Optional, List, Union
from datetime import date
from fields import fields

field_names = [field['field_name'] for field in fields]


class GeoPoint(BaseModel):
    """
    This schema represents a location on earth.
    """
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)


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
    datecollected: Optional[date] = None
    datemodified: Optional[date] = None
    earliestperiodorlowestsystem: Optional[str] = None
    etag: Optional[str] = None
    eventdate: Optional[str] = None
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
    scientificname: Optional[Union[str, List[str]]] = None
    specificepithet: Optional[str] = None
    stateprovince: Optional[Union[str, List[str]]] = None
    typestatus: Optional[str] = None
    uuid: Optional[str] = None
    verbatimeventdate: Optional[str] = None
    verbatimlocality: Optional[str] = None
    version: Optional[int] = None
    waterbody: Optional[str] = None


class LLMQueryOutput(BaseModel):
    """
    This schema represents the output containing the LLM-generated iDigBio query. 
    """
    rq: IDBQuerySchema = Field(...,
                               description="This is the iDigBio Query format and should contain the query generated "
                                           "from the user's plain text input.")
