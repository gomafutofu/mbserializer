# coding: utf-8

__author__ = 'Junki Ishida'

from .exceptions import ParseError
from ._compat import OrderedDict, raise_with_inner, PY3
from .utils import _to_dict, _parse_dict

try:
    import yaml
    from yaml.parser import ParserError

    try:
        from yaml.cyaml import (
            CSafeDumper as SafeDumper,
            CSafeLoader as Loader,
        )
    except ImportError:
        from yaml.dumper import (
            SafeDumper as SafeDumper,
            SafeLoader as Loader,
        )

    class Dumper(SafeDumper):
        def represent_ordereddict(self, data):
            return SafeDumper.represent_dict(self, data.items())

    Dumper.add_representer(OrderedDict, Dumper.represent_ordereddict)
    yaml_loaded = True
except:
    yaml_loaded = False


def _dump_yaml(model_class, data_type, data, **options):
    ordered = options.pop('ordered', True)
    if model_class._islist:
        _data = []
        for d in data or ():
            _data.append(_to_dict(model_class, data_type, d, ordered))
    else:
        _data = _to_dict(model_class, data_type, data, ordered)
    dumper = options.get('Dumper') or Dumper
    result = yaml.dump(_data, Dumper=dumper, **options)
    return result


def dump_yaml_str(model_class, data_type, data, **options):
    if PY3 and 'encoding' in options:
        options['encoding'] = None
    return _dump_yaml(model_class, data_type, data, **options)


def dump_yaml_bytes(model_class, data_type, data, **options):
    if options.get('encoding') is None:
        options['encoding'] = 'utf-8'
    return _dump_yaml(model_class, data_type, data, **options)


def load_yaml(model_class, data_type, data, **options):
    if PY3 and isinstance(data, bytes):
        encoding = options.get('encoding', 'utf-8')
        data = data.decode(encoding)
    loader = options.get('Loader', Loader)
    forcekey = options.get('forcekey', False)
    try:
        data = yaml.load(data, loader)
    except ParserError as e:
        raise_with_inner(ParseError, e)
    if model_class._islist:
        result = []
        for d in data:
            entity = _parse_dict(model_class, data_type, d, forcekey)
            result.append(entity)
        return result
    else:
        return _parse_dict(model_class, data_type, data, forcekey)
