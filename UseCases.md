# Examples

| Prompt                                                     | Result                                                                                                                                                                      |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Search for records**                                     |                                                                                                                                                                             |
| *Ursus arctos in North America*                            | Search for `{"scientificname": "Ursus arctos", "continent": "North America"}` Or maybe for `{"genus": "Ursus", "specificepithet": "arctos", "continent": "North America"}`? |
| *Bears*                                                    | Search for `{"family": "Ursidae"}`                                                                                                                                          |
|                                                            |                                                                                                                                                                             |
| **Questions about what's in iDigBio**                      |                                                                                                                                                                             |
| *How many records are in iDigBio?*                         | Search everything, report the "itemCount"                                                                                                                                   |
| *How many bear records are there in Florida?*              |                                                                                                                                                                             |
| *Which bear species has the most records?*                 | Search for bears, sort by itemCount, report the highest. This would be more straightforward if we query ElasticSearch directly.                                             |
|                                                            |                                                                                                                                                                             |
| **Biodiversity questions**                                 |                                                                                                                                                                             |
| *Are there bears in Florida?*                              |                                                                                                                                                                             |
| *What bear species live in Gainesville, FL?*               |                                                                                                                                                                             |
| *Have any bear species been observed in tropical regions?* |                                                                                                                                                                             |
|                                                            |                                                                                                                                                                             |
| **Taxonomy questions**                                     |                                                                                                                                                                             |
|                                                            |                                                                                                                                                                             |
| **iDigBio Portal usage questions**                         |                                                                                                                                                                             |
| What's the difference between data and indexTerms?         | Link to a wiki page and quote relevant text                                                                                                                                 |
| What does "verbatimLocality" mean?                         | Link to DarwinCore documentation and quote relevant text                                                                                                                    |

Unsolicited advice

| Prompt                         | Result                                                 |
|--------------------------------|--------------------------------------------------------|
| Something about "Acr saccarum" | Did you mean "Acer saccharum?"                         |
| Search for "Acer saccharum"    | Do you also want to include "Acer saccharum marshall"? |

# Goals

1. A quicker, easier-to-use alternative to the existing form-based search interface
    - As much as possible, allow users to express searches in shorthand, e.g. just type "Ursus arctos". Don't require
      the user to spell everything out.
2. Leverage LLM knowledge when requested/appropriate/helpful/trustworthy
    - Always flag LLM-generated information as such and run LLM-generated information by the user before incorporating
      it into searches/etc.
3. etc.

# Maybes

LLM enhancements to data discovery and navigation:

- When a scientific name is specified, offer to look for spelling variations and synonyms; always run results by the
  user before using them

Interface:

- Let's do what OpenAI does - only one panel with visualizations inserted into the conversation. With the static map and
  records list panels, it's not always obvious how they sync with the conversation.
-

# Notes

1. What considerations need to be made for raw vs. index values?
2. Geographically, records can confirm species presence (range), but not necessarily concentration (distribution)

# Example conversations

## Bears

User: How are bear occurrences geographically distributed?

Robot: [map common name "bear" to taxon "Ursidae" (family)]

Robot: [search iDigBio for {"family": "Ursidae"}]

Robot: Per ITIS, "bears" describes the taxonomic family "Ursidae". Most records are in North America (90%), specifically
Alaska (50%).

User: What are the top 2 bear species by record count?

Robot: [reuse search results]

Robot: The top two species by record count are tUrsus marthe poar"lar bearitimus" (the polar bear)a and "Ursus
arctos)" (the brown bear).