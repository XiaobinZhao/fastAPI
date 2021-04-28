from json import loads as json_loads


def json_serializer(s, **kw):
    if isinstance(s, bytes):
        return json_loads(s.decode('utf-8'), **kw)
    else:
        return json_loads(s, **kw)