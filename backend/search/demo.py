import json

import idigbio_util
import search
from nlp.agent import Agent


def run(agent: Agent, request: dict):
    if request["action"] == "generate_rq":
        response = search.api.generate_rq(agent, request)
    else:
        response = search.api.update_input(agent, request)

    if type(response["rq"]) == dict:
        rq = json.dumps(response["rq"])
    else:
        rq = response["rq"]

    url_params = idigbio_util.url_encode_params({"rq": response["rq"]})

    return {
        "portal_url": f"https://beta-portal.idigbio.org/portal/search?{url_params}",
        "api_url": f"https://search.idigbio.org/v2/search/records?{url_params}",
        "input": response["input"],
        "rq": rq,
        "message": response["message"]
    }
