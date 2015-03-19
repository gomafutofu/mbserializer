# coding: utf-8

__author__ = 'Junki Ishida'

import pytz
from .. import converters
from .._xml import _getxmlns
from .._compat import str_types, iteritems

import sys

class FieldBase(object):
    _dump_converters = None
    _parse_converters = None
    index = 0
    options = None

    def __init__(self, key=None, required=True, **options):
        self.key = key
        self._required = required
        self._isattr = False
        self._nullable = False
        self._istext = False
        self._isdelegate = False
        self._ismember = False
        self._islist = False
        self._islistdelegate = False
        self._hasparse = hasattr(self, 'parse')
        self._hasparse_json = hasattr(self, 'parse_json')
        self._hasparse_yaml = hasattr(self, 'parse_yaml')
        self._hasparse_xml = hasattr(self, 'parse_xml')
        self._hasdump = hasattr(self, 'dump')
        self._hasdump_json = hasattr(self, 'dump_json')
        self._hasdump_yaml = hasattr(self, 'dump_yaml')
        self._hasdump_xml = hasattr(self, 'dump_xml')
        self.index += 1
        FieldBase.index += 1

    @classmethod
    def register_dump_converter(cls, data_type, dump_converter):
        if cls._dump_converters is None:
            cls._dump_converters = {}
        cls._dump_converters[data_type] = dump_converter

    @classmethod
    def register_parse_converter(cls, data_type, load_converter):
        if cls._parse_converters is None:
            cls._parse_converters = {}
        cls._parse_converters[data_type] = load_converter

    def _dump(self, value, data_type):
        if self._dump_converters is not None:
            converter = self._dump_converters.get(data_type)
            if converter:
                value = converter(value, **self.options) if self.options else converter(value)
        return value

    def _parse(self, value, data_type):
        if self._parse_converters is not None:
            converter = self._parse_converters.get(data_type)
            if converter:
                value = converter(value, **self.options) if self.options else converter(value)
        return value

    def get_key(self, key, **options):
        return self.key or key


class TextField(FieldBase):
    def __init__(self, key=None, **options):
        super(TextField, self).__init__(key=key, required=True, **options)
        self._istext = True


class MemberFieldBase(FieldBase):
    def __init__(self, key=None, xmlns=None, required=True, **options):
        super(MemberFieldBase, self).__init__(key, required, **options)
        self.xmlns = xmlns
        self._ismember = True


class AttributeField(MemberFieldBase):
    def __init__(self, key=None, xmlns=None, required=True, **options):
        super(AttributeField, self).__init__(key, xmlns, required, **options)
        self._isattr = True


class ElementField(MemberFieldBase):
    def __init__(self, key=None, xmlns=None, required=True, nullable=False, **options):
        super(ElementField, self).__init__(key, xmlns, required, **options)
        self._nullable = nullable


class DelegateElement(ElementField):
    def __init__(self, model_class, xmlns=None, required=True, nullable=False, **options):
        super(DelegateElement, self).__init__(model_class.__tag__, _getxmlns(xmlns, model_class.__xmlns__),
                                              required, nullable, **options)
        self.model_class = model_class
        self._isdelegate = True


class ListField(ElementField):
    def __init__(self, tag, key=None, xmlns=None, elem_xmlns=None, required=True, nullable=False,
                 nested=False, **options):
        super(ListField, self).__init__(key, elem_xmlns, required, nullable, **options)
        self.tag = tag
        if not self.tag:
            raise ValueError()
        self._islist = True
        self.nested = nested
        self.nested_xmlns = xmlns


class DelegateList(ListField):
    def __init__(self, model_class, key=None, xmlns=None, elem_xmlns=None,
                 required=True, nullable=False, nested=False, **options):
        super(DelegateList, self).__init__(model_class.__tag__, key, _getxmlns(xmlns, model_class.__xmlns__),
                                           elem_xmlns, required, nullable, nested, **options)
        self.model_class = model_class
        self._islistdelegate = True


class StringFieldMixin(FieldBase): pass


class IntegerFieldMixin(FieldBase): pass


class FloatFieldMixin(FieldBase): pass


class BooleanFieldMixin(FieldBase): pass


class DecimalFieldMixin(FieldBase): pass


class DatetimeFieldMixin(FieldBase):
    __flexible_required = sys.version_info[:1] < (3, 2)

    def __init__(self, *args, **kwargs):
        super(DatetimeFieldMixin, self).__init__(*args, **kwargs)
        tz = kwargs.get('timezone')
        self.options = {
            'format': kwargs.get('format') or '%Y-%m-%dT%H:%M:%S%z',
            'timezone': pytz.timezone(tz) if isinstance(tz, str_types) else tz,
            'flexible': kwargs.get('flexible', self.__flexible_required),
        }


class DateFieldMixin(FieldBase):
    def __init__(self, *args, **kwargs):
        super(DateFieldMixin, self).__init__(*args, **kwargs)
        self.options = {
            'format': kwargs.get('format') or '%Y-%m-%d',
        }


class EnumFieldMixin(FieldBase):
    def __init__(self, *args, **kwargs):
        super(EnumFieldMixin, self).__init__(*args, **kwargs)
        values = kwargs.get('values')
        if len(values) == 0:
            raise ValueError()
        if any(v for v in values if not isinstance(v, str_types)):
            raise ValueError()
        self.options = {
            'values': frozenset(values)
        }


def _register_converters(converter_map):
    for field_class, map in iteritems(converter_map):
        if 'dump' in map:
            for converter, data_types in iteritems(map['dump']):
                for data_type in data_types:
                    field_class.register_dump_converter(data_type, converter)
        if 'parse' in map:
            for converter, data_types in iteritems(map['parse']):
                for data_type in data_types:
                    field_class.register_parse_converter(data_type, converter)


_json_types = ('json', 'json/str', 'json/bytes',)
_xml_types = ('xml', 'xml/str', 'xml/bytes',)
_yaml_types = ('yaml', 'yaml/str', 'yaml/bytes', )

_all_types = _json_types + _xml_types + _yaml_types

_register_converters(
    {
        StringFieldMixin: {
            'dump': {
                converters.str_to_str: _all_types,
            },
            'parse': {
                converters.str_to_str: _json_types + _yaml_types,
                converters.str_or_none_to_str: _xml_types,
            },
        },
        IntegerFieldMixin: {
            'dump': {
                converters.int_to_int: _json_types + _yaml_types,
                converters.int_to_str: _xml_types,
            },
            'parse': {
                converters.int_to_int: _json_types + _yaml_types,
                converters.str_to_int: _xml_types,
            },
        },
        FloatFieldMixin: {
            'dump': {
                converters.int_or_float_to_float: _json_types + _yaml_types,
                converters.int_or_float_to_str: _xml_types,
            },
            'parse': {
                converters.int_or_float_to_float: _json_types + _yaml_types,
                converters.str_to_float: _xml_types,
            },
        },
        BooleanFieldMixin: {
            'dump': {
                converters.bool_to_bool: _json_types + _yaml_types,
                converters.bool_to_str: _xml_types,
            },
            'parse': {
                converters.bool_to_bool: _json_types + _yaml_types,
                converters.str_to_bool: _xml_types,
            },
        },
        DecimalFieldMixin: {
            'dump': {
                converters.decimal_to_str: _all_types,
            },
            'parse': {
                converters.str_to_decimal: _all_types,
            },
        },
        DatetimeFieldMixin: {
            'dump': {
                converters.datetime_to_str: _all_types,
            },
            'parse': {
                converters.str_to_datetime: _all_types,
            },
        },
        DateFieldMixin: {
            'dump': {
                converters.date_to_str: _all_types,
            },
            'parse': {
                converters.str_to_date: _all_types,
            },
        },
        EnumFieldMixin: {
            'dump': {
                converters.enum_to_str: _all_types,
            },
            'parse': {
                converters.str_to_enum: _all_types,
            },
        },
    }
)


class StringText(TextField, StringFieldMixin):
    pass


class IntegerText(TextField, IntegerFieldMixin):
    pass


class FloatText(TextField, FloatFieldMixin):
    pass


class DecimalText(TextField, DecimalFieldMixin):
    pass


class BooleanText(TextField, BooleanFieldMixin):
    pass


class DatetimeText(TextField, DatetimeFieldMixin):
    def __init__(self, key=None, required=True, timezone=None, format=None, **options):
        super(DatetimeText, self).__init__(key, required, timezone=timezone, format=format, **options)


class DateText(TextField, DateFieldMixin):
    def __init__(self, key=None, required=True, format=None, **options):
        super(DateText, self).__init__(key, required, format=format, **options)


class EnumText(TextField, EnumFieldMixin):
    def __init__(self, values, key=None, **options):
        super(EnumText, self).__init__(key, values=values, **options)


class StringAttribute(AttributeField, StringFieldMixin): pass


class IntegerAttribute(AttributeField, IntegerFieldMixin): pass


class FloatAttribute(AttributeField, FloatFieldMixin): pass


class DecimalAttribute(AttributeField, DecimalFieldMixin): pass


class BooleanAttribute(AttributeField, BooleanFieldMixin): pass


class DatetimeAttribute(AttributeField, DatetimeFieldMixin):
    def __init__(self, key=None, xmlns=None, required=True, timezone=None, format=None, **options):
        super(DatetimeAttribute, self).__init__(key, xmlns, required, timezone=timezone, format=format, **options)


class DateAttribute(AttributeField, DateFieldMixin):
    def __init__(self, key=None, xmlns=None, required=True, format=None, **options):
        super(DateAttribute, self).__init__(key, xmlns, required, format=format, **options)


class EnumAttribute(AttributeField, EnumFieldMixin):
    def __init__(self, values, key=None, xmlns=None, required=True, **options):
        super(EnumAttribute, self).__init__(key, xmlns, required, values=values, **options)


class StringElement(ElementField, StringFieldMixin): pass


class IntegerElement(ElementField, IntegerFieldMixin): pass


class FloatElement(ElementField, FloatFieldMixin): pass


class DecimalElement(ElementField, DecimalFieldMixin): pass


class BooleanElement(ElementField, BooleanFieldMixin): pass


class DatetimeElement(ElementField, DatetimeFieldMixin):
    def __init__(self, key=None, xmlns=None, required=True, nullable=False,
                 timezone=None, format=None, **options):
        super(DatetimeElement, self).__init__(key, xmlns, required, nullable, timezone=timezone, format=format,
                                              **options)


class DateElement(ElementField, DateFieldMixin):
    def __init__(self, key=None, xmlns=None, required=True, nullable=False, format=None, **options):
        super(DateElement, self).__init__(key, xmlns, required, nullable, format=format, **options)


class EnumElement(ElementField, EnumFieldMixin):
    def __init__(self, values, key=None, xmlns=None, required=True, nullable=False, **options):
        super(EnumElement, self).__init__(key, xmlns, required, nullable, values=values, **options)


class StringList(ListField, StringFieldMixin): pass


class IntegerList(ListField, IntegerFieldMixin): pass


class FloatList(ListField, FloatFieldMixin): pass


class DecimalList(ListField, DecimalFieldMixin): pass


class BooleanList(ListField, BooleanFieldMixin): pass


class DatetimeList(ListField, DatetimeFieldMixin):
    def __init__(self, tag, key=None, xmlns=None, elem_xmlns=None, required=True, nullable=False, nested=False,
                 timezone=None, format=None, **options):
        super(DatetimeList, self).__init__(tag, key, xmlns, elem_xmlns, required, nullable, nested,
                                           timezone=timezone, format=format, **options)


class DateList(ListField, DateFieldMixin):
    def __init__(self, tag, key=None, xmlns=None, elem_xmlns=None, required=True, nullable=False, nested=False,
                 format=None, **options):
        super(DateList, self).__init__(tag, key, xmlns, elem_xmlns, required, nullable, nested, format=format,
                                       **options)


class EnumList(ListField, EnumFieldMixin):
    def __init__(self, tag, values, key=None, xmlns=None, elem_xmlns=None, required=True,
                 nullable=False, nested=False, **options):
        super(EnumList, self).__init__(tag, key, xmlns, elem_xmlns, required, nullable, nested, values=values,
                                       **options)