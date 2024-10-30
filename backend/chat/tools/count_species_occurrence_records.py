from collections.abc import Iterator

from chat.processes.idigbio_records_summary import IDigBioRecordsSummary
from chat.conversation import Conversation
from chat.messages import Message
from chat.tools.tool import Tool
from chat.utils.assistant import present_results
from nlp.ai import AI

DESCRIPTION = """\
Counts the total number of records in iDigBio matching the user's search criteria. Also
breaks the count down by a specified field (default: scientific name) to build top-N lists or to find unique record 
field values that were matched. Counts can be broken down by any of iDigBio's query fields, such as "country" or
"collector".

Here are some examples of building top-N lists:
- List the 10 species that have the most records in a country
- List the 5 countries that have the most records of a species
- List the 3 collectors who have recorded the most occurrences of a species

Here are some examples of finding unique values in matching records:
- List the continents that a species occurs in
- List different scientific names that have the same genus and specific epithet (e.g., scientific names with 
different authors)

Also returns the URL used to collect records counts from the iDigBio Summary API.
"""


class CountSpeciesOccurrenceRecords(Tool):
    schema = {
        "name": "count_species_occurrence_records",
        "description": DESCRIPTION
    }

    def call(self, ai: AI, history=Conversation([]), request: str = None, state=None) -> Iterator[Message]:
        search = IDigBioRecordsSummary(ai, history, request)
        yield search.make_message()
        yield present_results(ai, history, request, search.summarize())
