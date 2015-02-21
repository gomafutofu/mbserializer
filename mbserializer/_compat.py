# coding: utf-8

__author__ = 'Junki Ishida'

import sys
from datetime import datetime

PY2 = sys.version_info[0] == 2
PY26 = PY2 and sys.version_info[1] == 6
PY3 = sys.version_info[0] == 3

if PY2:
    str_types = (str, unicode,)
    unicode_type = unicode
    int_types = (int, long,)
    int_or_float_types = (int, long, float,)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    def raise_with_inner(error_class, inner, *args, **kwargs):
        raise error_class(inner=inner, *args, **kwargs)
else:
    str_types = (str,)
    unicode_type = str
    int_types = (int, )
    int_or_float_types = (int, float,)

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from ._compat3 import _raise_with_inner

    def raise_with_inner(error_class, inner, *args, **kwargs):
        _raise_with_inner(error_class(inner=inner, *args, **kwargs), inner)

if PY26:
    try:
        from ordereddict import OrderedDict
    except ImportError:
        pass
else:
    from collections import OrderedDict


def with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})
