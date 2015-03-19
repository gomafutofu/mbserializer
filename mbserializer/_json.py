# coding: utf-8

__author__ = 'Junki Ishida'

from .exceptions import ParseError
from .utils import _to_dict, _parse_dict
from ._compat import str_types, raise_with_inner, PY2, PY3

import json


def dump_json_str(model_class, data_type, data, **options):
    ordered = options.pop('ordered', True)
    if model_class._islist:
        _data = []
        for d in data or ():
            _data.append(_to_dict(model_class, data_type, d, ordered))
    else:
        _data = _to_dict(model_class, data_type, data, ordered)
    return json.dumps(_data, **options)


def dump_json_bytes(model_class, data_type, data, **options):
    result = dump_json_str(model_class, data_type, data, **options)
    if PY2 and isinstance(result, bytes):
        return result
    return result.encode('utf-8')


def load_json(model_class, data_type, data, **options):
    if PY3 and isinstance(data, bytes):
        data = data.decode('utf-8')
    if not isinstance(data, str_types):
        data = data.read()
    try:
        data = json.loads(data, **options)
    except ValueError as e:
        raise_with_inner(ParseError, e)
    forcekey = options.get('forcekey')
    if model_class._islist:
        result = []
        for d in data:
            entity = _parse_dict(model_class, data_type, d, forcekey)
            result.append(entity)
        return result
    else:
        return _parse_dict(model_class, data_type, data, forcekey)
