"""
Use case: help a user build a query like Shelly's:
    https://api.idigbio.org/v2/download/
    ?rq={"recordset":["2c00c297-9ebd-498a-b701-d3ebde4b49f3"]}
    &fields="data.dwc:scientificName","data.dwc:genus","data.dwc:specificEpithet","data.dwc:infraspecificEpithet",
    "uuid","data.dwc:occurrenceID","data.dwc:basisOfRecord","data.dwc:eventDate","data.dwc:year","data.dwc:month",
    "data.dwc:day","data.dwc:institutionCode","data.dwc:recordedBy","data.dwc:country","data.dwc:county",
    "data.dwc:stateProvince","data.dwc:locality","data.dwc:occurrenceRemarks","data.dwc:verbatimLocality",
    "data.dwc:decimalLatitude","data.dwc:verbatimLatitude","data.dwc:decimalLongitude","data.dwc:verbatimLongitude",
    "geopoint","data.dwc:coordinateUncertaintyInMeters","data.dwc:informationWithheld","data.dwc:habitat"}}

Search by iDigBio UUID
Return (almost) only data.dwc fields
- All taxonomy information genus and below
    "data.dwc:scientificName","data.dwc:genus","data.dwc:specificEpithet","data.dwc:infraspecificEpithet"
- Record IDs
    "uuid","data.dwc:occurrenceID"
- Basis of record
    "data.dwc:basisOfRecord"
- Collection date fields
    "data.dwc:eventDate","data.dwc:year","data.dwc:month","data.dwc:day"
- Collector/collection info
    "data.dwc:institutionCode","data.dwc:recordedBy"
- Location info
    "data.dwc:country","data.dwc:county","data.dwc:stateProvince","data.dwc:locality",
    "data.dwc:occurrenceRemarks","data.dwc:verbatimLocality","data.dwc:decimalLatitude",
    "data.dwc:verbatimLatitude","data.dwc:decimalLongitude","data.dwc:verbatimLongitude","geopoint",
    "data.dwc:coordinateUncertaintyInMeters"
"""
from chat_test.chat_test_util import chat


def test_list_record_id_fields():
    """
    "uuid","data.dwc:occurrenceID"
    """
    messages = chat("What fields can I use to identify records?")

    assert False


def test_the_whole_shebang():
    chat("I want to find records using iDigBio's records API")
    chat("What fields can I use to identify records?")
    chat("What fields describe how the observation was made?")
    chat("What fields contain collection date information?")
    chat("What fields describe who made the observation and/or collected the specimen?")
    chat("What fields describe location information?")
    messages = chat(
        "Generate a query that finds the recordset 2c00c297-9ebd-498a-b701-d3ebde4b49f3 and returns all fields that I "
        "just asked for.")

    assert False
