def string_must_contain(string, *substrings):
    matches = []
    misses = []
    for substring in substrings:
        if substring in string:
            matches += [substring]
        else:
            misses += [substring]

    if len(misses) > 0:
        raise AssertionError(f"""Missing expected substrings
        String: {string}
        Expected substrings: {substrings}
        Missing substrings:  {misses}""")
    return True
