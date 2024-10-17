import json

from idigbio_util import url_encode_params, percent_decode, percent_encode


def test_encode_url_with_nested():
    d = {"rq": {"name": "bob", "amount": 3.5}, "limit": 5}
    s = url_encode_params(d)
    assert s == "rq=%7B%22name%22:%22bob%22,%22amount%22:%223.5%22%7D&limit=5"


def test_encode_list():
    d = {"a_list": [1, 2]}
    s = url_encode_params(d)
    assert s == "a_list=[1,2]"


def test_percent_encode_json():
    d = {"rq": {"name": "bob", "amount": 3.5}, "limit": 5}
    s = percent_encode(json.dumps(d))
    assert s == "%7B%22rq%22:%20%7B%22name%22:%20%22bob%22,%20%22amount%22:%203.5%7D,%20%22limit%22:%205%7D"


def test_percent_decode_json():
    s = "%7B%22rq%22:%20%7B%22name%22:%20%22bob%22,%20%22amount%22:%203.5%7D,%20%22limit%22:%205%7D"
    d = json.loads(percent_decode(s))
    assert d == {"rq": {"name": "bob", "amount": 3.5}, "limit": 5}
