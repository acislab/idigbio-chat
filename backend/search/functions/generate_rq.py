from nlp.agent import Agent
from schema.idigbio.api import IDigBioRecordsApiParameters
from schema.idigbio.fields import fields
from search.data_types import Message, Result


def run(agent: Agent, data: dict) -> Message:
    user_input = data["input"]
    should_parse = check_if_user_input_is_on_topic(agent, user_input)

    if should_parse:
        params = search_species_occurrence_records(agent, [{
            "role": "user",
            "content": user_input
        }])

        return Message(
            input=user_input,
            rq=params["rq"],
            result=Result.success,
            message=""
        )
    else:
        return Message(
            input=user_input,
            rq={},
            result=Result.error,
            message="Failed to understand user input"
        )


SEARCH = {
    "name": "search_species_occurrence_records",
    "description": "Shows an interactive list of species occurrence records in iDigBio and a map of their "
                   "geographic distribution."
}

ABORT = {
    "name": "ask_an_expert",
    "description": "If none of the other tools satisfy the user's request, ask an expert for help."
}


def check_if_user_input_is_on_topic(agent, user_input) -> bool:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=None,
        max_tokens=100,
        functions=[SEARCH, ABORT],
        messages=[
            {
                "role": "system",
                "content": "You call functions to retrieve information that may help answer the user's "
                           "biodiversity-related queries. You do not answer queries yourself. If no other "
                           "functions match the user's query, call for help from an expert using the "
                           "ask_an_expert function."
            }, {
                "role": "user",
                "content": user_input
            }
        ]
    )

    fn_call = result.choices[0].message.function_call
    procedure_name = fn_call.name if fn_call is not None else ""
    return procedure_name == "search_species_occurrence_records"


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


def search_species_occurrence_records(agent: Agent, messages: list[dict]) -> dict:
    result = agent.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_model=IDigBioRecordsApiParameters,
        messages=[
                     {
                         "role": "system",
                         "content": SYSTEM_PROMPT
                     }
                 ] + messages,
    )

    params = result.model_dump(exclude_none=True, by_alias=True)
    return params
