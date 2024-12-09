from attr import dataclass
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying

from chat.content_streams import StreamedString
from chat.conversation import Conversation
from chat.processes.process import Process
from chat.utils.json import make_pretty_json_string
from idigbio_util import query_idigbio_api, make_idigbio_api_url, make_idigbio_portal_url
from nlp.ai import AI, StopOnTerminalErrorOrMaxAttempts, AIGenerationException
from schema.idigbio.api import IDigBioRecordsApiParameters
from schema.idigbio.fields import fields


@dataclass
class Results(dict):
    params: dict
    record_count: int
    api_query_url: str
    portal_url: str


class IDigBioRecordsSearch(Process):
    process_summary = "Searching iDigBio..."

    def __run__(self, ai: AI, conversation, request: str) -> StreamedString:
        try:
            params = _generate_records_search_parameters(ai, conversation, request)
        except AIGenerationException as e:
            yield self.note(e.message)
            return

        yield self.note(f"Generated search parameters:\n```json\n{make_pretty_json_string(params)}\n```")

        records_api_url = make_idigbio_api_url("/v2/search/records")
        self.note(f"Sending a POST request to the iDigBio records API at {records_api_url}")

        response_code, success, response_data = query_idigbio_api("/v2/search/records", params)
        record_count = response_data.get("itemCount", 0)

        if success:
            self.note(f"Response code: {response_code}")
        else:
            yield self.note(f"\n\nResponse code: {response_code} - something went wrong!")
            return

        api_query_url = make_idigbio_api_url("/v2/search/records", params)
        yield f"\n\n[View {record_count} matching records]({api_query_url})"
        self.note(f"The API query matched {record_count} records in iDigBio using the URL {api_query_url}")

        portal_url = make_idigbio_portal_url(params)
        yield f" | [Show in iDigBio portal]({portal_url})"
        self.note(
            f"The records can be viewed in the iDigBio portal at {portal_url}. The portal shows the records in an "
            f"interactive list and plots them on a map. The raw records returned returned by the API can be found at "
            f"{api_query_url}"
        )

        self.set_results(Results(
            params=params,
            record_count=record_count,
            api_query_url=api_query_url,
            portal_url=portal_url
        ))


def _generate_records_search_parameters(ai: AI, conversation: Conversation, request: str) -> dict:
    try:
        result = ai.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            response_model=IDigBioRecordsApiParameters,
            messages=conversation.render_to_openai(system_message=SYSTEM_PROMPT,
                                                   request=request),
            max_retries=Retrying(stop=StopOnTerminalErrorOrMaxAttempts(3))
        )
    except InstructorRetryException as e:
        raise AIGenerationException(e)

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params


FIELDS_DOC = "\n".join(f"{f['field_name']}: {f['field_type']}" for f in fields)

IDIGBIO_QUERY_FORMAT_DOC = """
# iDigBio Query Format

The iDigBio query format is intended to be an easy to write query format for our APIs. Its basic structure consists 
of a JSON dictionary, with zero or more top-level keys that reference fields in our indexes. (See: [Index Fields](
Index-Fields))

A basic multi-field query looks like this:
```json
{
    "scientificname": {
        "type": "exists"
    },
    "family": "asteraceae"
}
```
That query will look for anything in the family Asteraceae that also has the scientific name field populated.

Multiple fields are combined with the "AND" operator.

More details on the query types supported below. Note, the query types under all fields should work on any field in 
the index, including the non-string fields. The query types under the other sections will only work with fields of 
the matching type.

## All Fields

### Searching for a field being present in the record
```json
{
  "scientificname": {
    "type": "exists"
  }
}
```

### Searching for a field being absent in the record
```json
{
  "scientificname": {
    "type": "missing"
  }
}
```

### Full text searching
```json
{
  "data": {
    "type": "fulltext",
    "value": "aster"
  }
}
```

### Searching for a value within a field
```json
{
  "family": "asteraceae"
}
```

### Searching for multiple values within a field
```json
{
  "family": [
    "asteraceae",
    "fagaceae"
  ]
}
```

### Searching for a value by prefix
```json
{
  "family": {
    "type": "prefix",
    "value": "aster"
  }
}
```
## Boolean Fields

### Searching for a boolean value
```json
{
  "hasImage": true
}
```

## Numeric Fields

### Searching within a range for a numeric field
```json
{
  "minelevation": {
    "type": "range",
    "gte": "100",
    "lte": "200"
  }
}
```

## Date Fields

### Searching within a range on a date field
```json
{
  "datecollected": {
    "type": "range",
    "gte": "1800-01-01",
    "lte": "1900-01-01"
  }
}
```

## Geographic Point Fields

### Searching within a bounding box on a point field
```json
{
  "geopoint": {
    "type": "geo_bounding_box",
    "top_left": {
      "lat": 19.23,
      "lon": -130
    },
    "bottom_right": {
      "lat": -45.1119,
      "lon": 179.99999
    }
  }
}
```

### Searching within a radius around a geopoint
```json
{
  "geopoint": {
    "type": "geo_distance",
    "distance": "100km",
    "lat": -41.1119,
    "lon": 145.323
  }
}
```
"""

SYSTEM_PROMPT = f"""
You translate user requests into parameters for the iDigBio record search API.

# Query format

Here is a description of how iDigBio queries are formatted:

{IDIGBIO_QUERY_FORMAT_DOC} 

# Fields

Here is the list of fields that are defined:

{FIELDS_DOC}

# Examples

If the user specifies a binomial scientific name, try to break it up into its genus and specific epithet. However, 
if the user specifies that they want to search for an exact scientific name, use the "scientificname" field. If the 
user places something in quotes, use the full text that is quoted, do not break it up.

## Example 1

User: "Homo sapiens"
You: {{
    "genus": "Homo",
    "specificepithet: "sapiens"
}}

## Example 2

User: "Only Homo sapiens Linnaeus, 1758"
You: {{
    "scientificname": "Homo sapiens Linnaeus, 1758"
}}

## Example 3 - 

User: "Scientific name \"this is fake but use it anyway\""
You: {{
    "scientificname": "this is fake but use it anyway"
}}

## Example 4 - only records that specify a given field

User: "kingdom must be specified"
You: {{
    "kingdom": {{
        "type": "exists"
    }}
}}

## Example 5 - strings can be specified as lists

User: "Homo sapiens and Rattus rattus in North America and Australia"
You: {{
    "scientificname": ["Homo sapiens", "Rattus rattus],
    "continent": ["North America", "Australia"]
}}

## Example 6 - only match records that specify a field

User: "Records with a common name"
You {{
    "commonname": {{
        "type": "exists"
    }}
}}

## Example 7 - only match records that do NOT specify a field

User: "Records with no family classification"
You {{
    "family": {{
        "type": "missing"
    }}
}}

## Example 8 - records with boolean fields

User: "Records with no family classification"
You {{
    "family": {{
        "type": "missing"
    }}
}}
"""
