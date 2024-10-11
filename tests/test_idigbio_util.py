from idigbio_util import url_encode_params


def test_quote():
    d = {"rq": {"name": "bob", "amount": 3.5}, "limit": 5}
    s = url_encode_params(d)
    assert s == 'rq={"name":"bob","amount":3.5}&limit=5'


def test_encode_list():
    d = {"a_list": [1, 2]}
    s = url_encode_params(d)
    assert s == "a_list=[1,2]"
