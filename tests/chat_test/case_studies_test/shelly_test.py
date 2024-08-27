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

For the following recordsets (that exceed 100,000 records):
+-------------------------------------------------------------------------------+--------------------------------------+
| institutionCode	                                                            | recordset
+-------------------------------------------------------------------------------+--------------------------------------+
| UT	                                                                        | 2c00c297-9ebd-498a-b701-d3ebde4b49f3
| University of New Hampshire                                                   | 7644703a-ce24-4f7b-b800-66ddf8812f86
| UCMS                                                                      	| 8919571f-205a-4aed-b9f2-96ccd0108e4c
| IND	                                                                        | 0dab1fc7-ca99-456b-9985-76edbac003e0
| MNA	                                                                        | 49153f74-2969-4a6a-a145-309fcb970308
| C.A. Triplehorn Insect Collection, Ohio State University, Columbus, OH (OSUC)	| fc628e53-5fdf-4436-9782-bf637d812b48
| WIS	                                                                        | 58402fe3-37c1-4d15-9e07-0ff1c4c9fb11
| University of Central Florida Collection of Arthopods (UCFC)                  | 84006c59-fead-4b84-b3b5-cedf28f67ea9
+-------------------------------------------------------------------------------+--------------------------------------+
"""
from chat_test.chat_test_util import chat


def test_list_record_id_fields():
    """
    "uuid","data.dwc:occurrenceID"
    """
    messages = chat("What fields are used in recordset 2c00c297-9ebd-498a-b701-d3ebde4b49f3?")

    assert False


def test_the_whole_shebang():
    chat("What fields are used in recordset 2c00c297-9ebd-498a-b701-d3ebde4b49f3?")
    chat("What fields can I use to identify records?")
    chat("What fields describe how the observation was made?")
    chat("What fields contain collection date information?")
    chat("What fields describe who made the observation and/or collected the specimen?")
    chat("What fields describe location information?")
    messages = chat(
        "Generate a search query that finds the recordset  and returns all "
        "fields that I just asked for.")

    assert False
