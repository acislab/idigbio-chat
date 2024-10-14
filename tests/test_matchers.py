import pytest

from matchers import string_must_contain


def test_string_must_contain():
    with pytest.raises(AssertionError):
        assert string_must_contain("this should", "fail")
