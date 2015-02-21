# coding: utf-8

__author__ = 'Junki Ishida'

from ._json import dump_json_str, dump_json_bytes, load_json
from ._xml import lxml_loaded, defusedxml_loaded, dump_xml_str, dump_xml_bytes, load_xml
from ._yaml import yaml_loaded, dump_yaml_str, dump_yaml_bytes, load_yaml


class Serializer(object):
    __load_funcs = {}
    __dump_funcs = {}

    def __init__(self, model_class, default_data_type='json', *args, **kwargs):
        self.model_class = model_class
        self.default_data_type = default_data_type

    @classmethod
    def register_load_func(cls, data_type, load_func):
        cls.__load_funcs[data_type] = load_func

    @classmethod
    def register_dump_func(cls, data_type, dump_func):
        cls.__dump_funcs[data_type] = dump_func

    def loads(self, data, data_type=None, **options):
        data_type = self.default_data_type if data_type is None else data_type
        return self.__load_funcs[data_type](self.model_class, data_type, data, **options)

    def dumps(self, data, data_type=None, **options):
        data_type = self.default_data_type if data_type is None else data_type
        return self.__dump_funcs[data_type](self.model_class, data_type, data, **options)


Serializer.register_dump_func('json', dump_json_str)
Serializer.register_dump_func('json/str', dump_json_str)
Serializer.register_dump_func('json/bytes', dump_json_bytes)

Serializer.register_load_func('json', load_json)
Serializer.register_load_func('json/str', load_json)
Serializer.register_load_func('json/bytes', load_json)

if lxml_loaded:
    Serializer.register_dump_func('xml', dump_xml_str)
    Serializer.register_dump_func('xml/str', dump_xml_str)
    Serializer.register_dump_func('xml/bytes', dump_xml_bytes)

if defusedxml_loaded:
    Serializer.register_load_func('xml', load_xml)
    Serializer.register_load_func('xml/str', load_xml)
    Serializer.register_load_func('xml/bytes', load_xml)

if yaml_loaded:
    Serializer.register_dump_func('yaml', dump_yaml_str)
    Serializer.register_dump_func('yaml/str', dump_yaml_str)
    Serializer.register_dump_func('yaml/bytes', dump_yaml_bytes)

    Serializer.register_load_func('yaml', load_yaml)
    Serializer.register_load_func('yaml/str', load_yaml)
    Serializer.register_load_func('yaml/bytes', load_yaml)

__all__ = ['Serializer', ]