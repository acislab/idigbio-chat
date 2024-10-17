import http.client
from typing import Sized, Union

import requests


def url_encode_inner(x):
    if type(x) == dict:
        return "{" + ",".join([f'"{k}":{url_encode_inner(v)}' for k, v in x.items()]) + "}"
    elif type(x) == list:
        return "[" + ",".join([url_encode_inner(v) for v in x]) + "]"
    elif type(x) == str:
        return f'"{x}"'
    elif type(x) == int:
        return str(x)
    else:
        return f'"{str(x)}"'


def url_encode_params(d: dict) -> str:
    d = sanitize_json(d)
    return percent_encode("&".join([f"{k}={url_encode_inner(v)}" for k, v in d.items()]))


PERCENT_ENCODING = [
    ("{", "%7B"),
    ("}", "%7D"),
    ("\"", "%22"),
    (" ", "%20")
]


def percent_encode(s: str):
    for codec in PERCENT_ENCODING:
        s = s.replace(codec[0], codec[1])
    return s


def percent_decode(s: str):
    for codec in PERCENT_ENCODING:
        s = s.replace(codec[1], codec[0])
    return s


JSON = Union[dict, list, str, int, float]


def sanitize_json(data: JSON) -> JSON:
    if isinstance(data, dict):
        return {k: sanitize_json(v) for k, v in data.items() if not _is_empty(v)}
    elif isinstance(data, list):
        return [sanitize_json(v) for v in data if not _is_empty(v)]
    elif isinstance(data, int | float):
        return data
    else:
        return str(data)


def _is_empty(data):
    return len(data) == 0 if isinstance(data, Sized) else False


def query_idigbio_api(endpoint: str, params: dict) -> (str, bool, dict):
    params = sanitize_json(params)
    api_url = make_idigbio_api_url(endpoint)
    response = requests.post(api_url, json=params)
    code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
    return code, response.ok, response.json()


def make_idigbio_portal_url(params: dict = None):
    url_params = "" if params is None else "?" + url_encode_params(params)
    return f"https://portal.idigbio.org/portal/search{url_params}"


def make_idigbio_api_url(endpoint: str, params: dict = None) -> str:
    url_params = "" if params is None else "?" + url_encode_params(params)
    return f"https://search.idigbio.org{endpoint}{url_params}"
