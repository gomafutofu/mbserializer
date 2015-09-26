# coding: utf-8

__author__ = 'Junki Ishida'

from .exceptions import FormatError
from .declarations import NotExist, Entity
from ._compat import iteritems, OrderedDict

try:
    from lxml.etree import QName
except ImportError:
    from xml.etree.ElementTree import QName


def haskey(data, key, isdict):
    if isdict:
        return key in data
    return hasattr(data, key)


def getvalue(data, key, isdict, default=None):
    if isdict:
        return data.get(key, default)
    return getattr(data, key, default)


def _to_dict(model_class, data_type, data, ordered):
    isdict = isinstance(data, dict)
    result = OrderedDict() if ordered else {}
    for k, f in iteritems(model_class._fields):
        if not haskey(data, k, isdict):
            if not f._required:
                continue
            raise FormatError('"{0}" is not found.'.format(k))
        src = getvalue(data, k, isdict)
        if not f._required and src is NotExist:
            continue
        if f._nullable and src is None:
            value = None
        else:
            if f._islist:
                value = []
                for v in src:
                    item = _to_dict(f.model_class, data_type, v, ordered) \
                        if f._islistdelegate else f._dump(v, data_type)
                    value.append(item)
            else:
                value = _to_dict(f.model_class, data_type, src, ordered) \
                    if f._isdelegate else f._dump(src, data_type)
        result[f.get_key(k)] = value
    return result


def _parse_dict(model_class, data_type, data, forcekey):
    entity = Entity()
    for k, f in model_class._fields.items():
        key = f.get_key(k)
        if not key in data:
            if not f._required:
                if forcekey:
                    entity[k] = NotExist
                continue
            raise FormatError()
        src = data[key]
        if f._nullable and src is None:
            value = None
        else:
            if f._islist:
                value = []
                if src is not None:
                    for v in src:
                        item = _parse_dict(f.model_class, data_type, v, forcekey) \
                            if f._islistdelegate else f._parse(v, data_type)
                        value.append(item)
            else:
                value = _parse_dict(f.model_class, data_type, src, forcekey) \
                    if f._isdelegate else f._parse(src, data_type)
        entity[k] = value
    return entity
