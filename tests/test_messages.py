import json

from chat_test.messages import ColdMessage


def test_pack():
    cm = ColdMessage(**{'name': 'Wilma', 'age': 50, 'alive': True, 'friends': ['Fred', 'Bambam']})
    raw = cm.stringify()
    assert raw == '{"name": "Wilma", "age": 50, "alive": true, "friends": ["Fred", "Bambam"]}'


def test_unpack():
    raw = '{"name": "Wilma", "age": 50, "alive": true, "friends": ["Fred", "Bambam"]}'
    cm = ColdMessage(json.loads(raw))
    assert cm.read_all() == {'name': 'Wilma', 'age': 50, 'alive': True, 'friends': ['Fred', 'Bambam']}
