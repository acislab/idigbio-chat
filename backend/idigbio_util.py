def url_encode_value(x):
    if type(x) == str:
        return f'"{x}"'
    else:
        return str(x)


def url_encode_inner(x):
    if type(x) == dict:
        return "{" + ",".join([f'"{k}":{url_encode_inner(v)}' for k, v in x.items()]) + "}"
    elif type(x) == str:
        return f'"{x}"'
    else:
        return str(x)


def url_encode_params(d):
    return "&".join([f"{k}={url_encode_inner(v)}" for k, v in d.items()])
