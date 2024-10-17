import re
from typing import Sized

import pytest

import idigbio_util
from chat.conversation import Conversation
from chat.messages import UserMessage, Message


def repeat(n):
    print()  # pytest stdout doesn't end on a new line
    for i in range(0, n):
        print(f"  Attempt {i}")
        yield n


def test_conversation(m: str | Message | list[Message]):
    conv = Conversation()

    if isinstance(m, str):
        m = UserMessage(m)

    if isinstance(m, Message):
        m = [m]

    for m in m:
        conv.append(m)

    return conv


def clean(data: dict):
    if not isinstance(data, dict):
        return data
    else:
        return {k: clean(v) for k, v in data.items() if not is_empty(v)}


def is_empty(data):
    return len(data) == 0 if isinstance(data, Sized) else False


def clean_string(s: str):
    # Ignore soft wraps by linter
    s = s.replace("\n\n", "DOUBLE_BREAK")
    s = s.replace("\n", "")
    s = s.replace("DOUBLE_BREAK", "\n\n")

    s = idigbio_util.percent_decode(s)
    return s.strip()


def fit_string(string: str, template: str):
    """
    If the string matches the template, returns the string. Otherwise, returns the template. Equating string with the
    returned value will prompt IntelliJ to give a detailed diff.

    Example usage:
        template =
        my_string = "My uncle's name is Bob"
        assert my_string == fit_string(my_string, template)

        # Assertion error: "My uncle's name is Bob" != "My name is {word}"
        # Expected :'My name is {word}'
        # Actual   :"My uncle's name is Bob"
        # <Click to see difference>
    """
    test_string = string
    re_template = template

    # Make the template safe to escape without losing placeholders
    for sub in [
        ("{", "LEFT_BRACKET"),
        ("}", "RIGHT_BRACKET")
    ]:
        re_template = re_template.replace(*sub)

    re_template = re.escape(re_template)

    # Now substitute placeholders
    for sub in [
        ("LEFT_BRACKET", "{"),
        ("RIGHT_BRACKET", "}"),
        ("{word}", r'[\w,]+')
    ]:
        re_template = re_template.replace(*sub)  # Ignore soft wraps by linter

    match = re.fullmatch(re_template, test_string)
    return string if match else template


def assert_string_matches_template(string: str, template: str):
    s = clean_string(string)
    t = clean_string(template)
    assert s == fit_string(s, t)


def test_fit_string_with_percents():
    my_string = "My name is %22Bob%22"
    assert my_string == fit_string(my_string, "My name is \"{word}\"")


def test_fit_string_that_matches():
    my_string = "My name is Bob"
    assert my_string == fit_string(my_string, "My name is {word}")


@pytest.mark.fail
def test_fit_string_that_doesnt_match():
    template = "My name is {word}"
    my_string = "My uncle's name is Bob"
    assert my_string == fit_string(my_string, template)
