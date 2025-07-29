def get_nested(data, *keys, default=None):
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data
