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
    return "&".join([f"{k}={url_encode_inner(v)}" for k, v in d.items()]) \
        .replace("{", "%7B") \
        .replace("}", "%7D") \
        .replace("\"", "%22") \
        .replace(" ", "%20")
