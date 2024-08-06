# Examples

| Prompt                                             | Result                                                                       |
|----------------------------------------------------|------------------------------------------------------------------------------|
| Ursus arctos in North America                      | Search for `{"scientificname": "Ursus arctos", "continent": "North America`} |
| Bears                                              | Search for `{"family": "Ursidae"}`                                           |
| What's the difference between data and indexTerms? | Point to a wiki page and quote relevant text                                 |

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