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
    else:
        return hasattr(data, key)


def getvalue(data, key, isdict, default=None):
    if isdict:
        return data.get(key, default)
    else:
        return getattr(data, key, default)


def getxmlns(arg, default):
    if arg == '':
        return arg
    return arg or default


def gettag(tag, xmlns):
    if xmlns:
        return str(QName(xmlns, tag))
    return tag


def getnsmap(xmlnsset, xmlnsmap, rootxmlns):
    nsmap = {}
    for xmlns in xmlnsset:
        if xmlns == rootxmlns:
            nsmap[None] = xmlns
        elif xmlns in xmlnsmap:
            nsmap[xmlnsmap[xmlns]] = xmlns
    return nsmap


def _setfields(fields, attrs):
    from .fields.declarations import FieldBase, TextField

    _attrs = []
    hastext = False
    for k, v in iteritems(attrs):
        if isinstance(v, FieldBase):
            _attrs.append((k, v,))
        elif isinstance(v, type) and issubclass(v, FieldBase):
            _attrs.append((k, v(),))
    for k, v in sorted(_attrs, key=lambda a: a[1].index):
        if isinstance(v, TextField):
            if hastext:
                raise FormatError()
            else:
                hastext = True
        fields[k] = v


NILTAG = gettag('nil', 'http://www.w3.org/2001/XMLSchema-instance')


def isnil(element):
    return element.text is None and NILTAG in element.attrib and element.attrib[NILTAG] == 'true'


def setnil(element):
    element.attrib[NILTAG] = 'true'


def _to_dict(model_class, data_type, data, ordered):
    isdict = isinstance(data, dict)
    result = OrderedDict() if ordered else {}
    for k, f in iteritems(model_class._fields):
        if not haskey(data, k, isdict):
            if f._ignorable:
                continue
            raise FormatError('"{0}" is not found.'.format(k))
        src = getvalue(data, k, isdict)
        if f._ignorable and src is NotExist:
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


def _parse_dict(model_class, data_type, data):
    entity = Entity()
    for k, f in model_class._fields.items():
        key = f.get_key(k)
        if not key in data:
            if f._ignorable:
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
                        item = _parse_dict(f.model_class, data_type, v) \
                            if f._islistdelegate else f._parse(v, data_type)
                        value.append(item)
            else:
                value = _parse_dict(f.model_class, data_type, src) \
                    if f._isdelegate else f._parse(src, data_type)
        entity[k] = value
    return entity
