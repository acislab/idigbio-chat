# from chat.tools.tool import Tool
# from chat.conversation import Conversation, Message, AiProcessingMessage, AiChatMessage
# import pandas as pd
#
#
# class SpeciesEndangeredStatus(Tool):
#     """
#     Responds with a string containing the endangered status of a genus + specificEpithet.
#     """
#     schema = {
#         "name": "species_endangered_status",
#         "description": "Determines if a species is endangered or not based on the user provided genus and "
#                        "specificepithet."
#     }
#
#     verbal_return_type = "the endangered status of a species"
#
#     def call(self, agent: Agent, history=Conversation([]), request: str, state=None) -> Iterator[Message]:
#         status = _get_threat_status()
#
#
# def _build_df_from_files():
#     df = pd.read_csv('distribution.txt', sep='\t', names=columns)
#     df_taxon = pd.read_csv('taxon.txt', sep='\t', names=columns_taxon)
#     df["scientificname"] = df_taxon["genus"] + " " + df_taxon["specificEpithet"]
#     return df
#
#
# def _get_threat_status(scientific_name):
#     # Filter the DataFrame for the specific scientific name
#     df = _build_df_from_files()
#     result = df[df['scientificname'].str.lower() == scientific_name.lower()]
#
#     if result.empty:
#         return f"No data found for {scientific_name}"
#     else:
#         # Return the threat status
#         return result['threatStatus'].iloc[0]
